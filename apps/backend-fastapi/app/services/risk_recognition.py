from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import session_scope
from app.models import (
    ElderFamilyBinding,
    NotificationRecord,
    RiskAlert,
    RiskLexiconTerm,
    RiskRule,
    SmsRecognitionRecord,
    CallRecognitionRecord,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
)

RISK_LEVEL_SCORE = {"low": 30, "medium": 65, "high": 90}
RISK_LEVEL_PRIORITY = {"low": 1, "medium": 2, "high": 3}
AUDIO_GUARD_RULE_CODE = "AI_AUDIO_MODEL"
AUDIO_GUARD_MIN_DURATION_SECONDS = 60
AUDIO_FRAUD_RESULT_TO_RISK_LEVEL = {
    "非诈骗": "low",
    "疑似诈骗": "medium",
    "诈骗": "high",
}

DEFAULT_LEXICON_TERMS = [
    {"term": "验证码", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信验证码索取高危词"},
    {"term": "点击链接", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信诱导点击链接"},
    {"term": "短链接", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信短链跳转"},
    {"term": "退款", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "退款补偿类诈骗"},
    {"term": "补偿", "category": "sms_keyword", "scene": "sms", "risk_level": "medium", "notes": "客服补偿诱导"},
    {"term": "中奖", "category": "sms_keyword", "scene": "sms", "risk_level": "medium", "notes": "中奖领奖类诈骗"},
    {"term": "银行卡冻结", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "冒充银行风控"},
    {"term": "安全账户", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "冒充公检法高危话术"},
    {"term": "配合调查", "category": "call_phrase", "scene": "call", "risk_level": "medium", "notes": "施压调查话术"},
    {"term": "不要告诉家人", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "隔离受害者常见话术"},
    {"term": "转到指定账户", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "诱导转账"},
    {"term": "远程共享屏幕", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "远控协助诈骗"},
    {"term": "刷流水", "category": "call_phrase", "scene": "call", "risk_level": "medium", "notes": "刷单刷流水骗局"},
]

DEFAULT_RULES = [
    {
        "code": "SMS_REFUND_LINK",
        "name": "短信退款链接识别",
        "scene": "sms",
        "risk_level": "high",
        "priority": 10,
        "trigger_terms": ["退款", "点击链接"],
        "reason_template": "短信同时出现退款补偿和链接跳转信息，疑似冒充客服引导点击诈骗页面。",
        "suggestion_template": "不要点击链接，不要继续填写个人信息，先联系子女或官方客服核实。",
    },
    {
        "code": "SMS_VERIFY_CODE",
        "name": "短信验证码索取识别",
        "scene": "sms",
        "risk_level": "high",
        "priority": 20,
        "trigger_terms": ["验证码"],
        "reason_template": "短信要求提供验证码，存在盗取账号或支付验证信息风险。",
        "suggestion_template": "不要向任何人透露验证码，建议立即删除短信并联系家属确认。",
    },
    {
        "code": "SMS_PRIZE_TRAP",
        "name": "短信中奖诱导识别",
        "scene": "sms",
        "risk_level": "medium",
        "priority": 30,
        "trigger_terms": ["中奖"],
        "reason_template": "短信存在中奖领奖诱导，常见于引导转账或填写隐私信息骗局。",
        "suggestion_template": "不要轻信中奖信息，不要缴纳任何手续费。",
    },
    {
        "code": "CALL_POLICE_IMPERSONATION",
        "name": "冒充公检法来电",
        "scene": "call",
        "risk_level": "high",
        "priority": 10,
        "trigger_terms": ["安全账户", "配合调查"],
        "reason_template": "通话出现安全账户和配合调查等话术，符合冒充公检法诈骗特征。",
        "suggestion_template": "立即挂断，通过官方公布电话回拨核实，不要转账。",
    },
    {
        "code": "CALL_ISOLATION_PRESSURE",
        "name": "通话隔离施压识别",
        "scene": "call",
        "risk_level": "high",
        "priority": 15,
        "trigger_terms": ["不要告诉家人"],
        "reason_template": "来电方要求不要告诉家人，属于典型诈骗隔离受害者手法。",
        "suggestion_template": "结束通话后马上联系家属或社区人员，不要独自处理。",
    },
    {
        "code": "CALL_TRANSFER_GUIDE",
        "name": "通话转账诱导识别",
        "scene": "call",
        "risk_level": "high",
        "priority": 20,
        "trigger_terms": ["转到指定账户", "远程共享屏幕"],
        "reason_template": "通话包含指定账户转账或共享屏幕要求，存在资金被盗风险。",
        "suggestion_template": "不要转账，不要开启屏幕共享，建议立即联系家属。",
    },
]

DEFAULT_RULE_TERMS_BY_CODE = {
    item["code"]: list(item["trigger_terms"])
    for item in DEFAULT_RULES
}


@dataclass
class MatchedRule:
    code: str
    name: str
    risk_level: str
    priority: int
    hit_terms: list[str]
    reason_template: str
    suggestion_template: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _ensure_elder_exists(session, elder_user_id: str) -> User:
    elder = session.get(User, elder_user_id)
    if not elder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="老人用户不存在")
    return elder


def _load_lexicon_terms(session, scene: str) -> list[RiskLexiconTerm]:
    items = session.execute(
        select(RiskLexiconTerm)
        .where(RiskLexiconTerm.scene == scene, RiskLexiconTerm.status == "enabled")
        .order_by(RiskLexiconTerm.term.asc())
    ).scalars().all()
    if items:
        return items
    return [
        RiskLexiconTerm(
            id=f"default-lex-{scene}-{index}",
            term=item["term"],
            category=item["category"],
            scene=item["scene"],
            risk_level=item["risk_level"],
            status="enabled",
            source="builtin",
            notes=item["notes"],
        )
        for index, item in enumerate(DEFAULT_LEXICON_TERMS, start=1)
        if item["scene"] == scene
    ]


def _parse_trigger_terms(rule: RiskRule) -> list[str]:
    expression = (rule.trigger_expression or "").replace("&&", ",").replace("||", ",")
    parts = [part.strip() for part in expression.split(",") if part.strip()]
    terms: list[str] = []
    for part in parts:
        if "contains(" in part and ")" in part:
            term = part.split("contains(", 1)[1].split(")", 1)[0]
            term = term.strip().strip("'\"")
            if term:
                terms.append(term)
    return terms


def _looks_like_placeholder_terms(terms: list[str]) -> bool:
    if not terms:
        return True
    for term in terms:
        if any(ord(char) > 127 for char in term):
            return False
    return True


def _load_rules(session, scene: str) -> list[MatchedRule]:
    rows = session.execute(
        select(RiskRule)
        .where(RiskRule.scene == scene, RiskRule.status == "enabled")
        .order_by(RiskRule.priority.asc())
    ).scalars().all()
    matched_rules: list[MatchedRule] = []
    loaded_codes: set[str] = set()
    if rows:
        for row in rows:
            hit_terms = _parse_trigger_terms(row)
            if _looks_like_placeholder_terms(hit_terms):
                hit_terms = DEFAULT_RULE_TERMS_BY_CODE.get(row.code, [])
            matched_rules.append(
                MatchedRule(
                    code=row.code,
                    name=row.name,
                    risk_level=row.risk_level,
                    priority=row.priority,
                    hit_terms=hit_terms,
                    reason_template=row.reason_template or "",
                    suggestion_template=row.suggestion_template or "",
                )
            )
            loaded_codes.add(row.code)

    for item in DEFAULT_RULES:
        if item["scene"] != scene or item["code"] in loaded_codes:
            continue
        matched_rules.append(
            MatchedRule(
                code=item["code"],
                name=item["name"],
                risk_level=item["risk_level"],
                priority=item["priority"],
                hit_terms=list(item["trigger_terms"]),
                reason_template=item["reason_template"],
                suggestion_template=item["suggestion_template"],
            )
        )
    return matched_rules


def _detect_terms(text: str, lexicon_terms: list[RiskLexiconTerm]) -> tuple[list[str], str]:
    normalized = text.lower()
    matched_terms: list[str] = []
    max_level = "low"
    for term in lexicon_terms:
        if term.term.lower() in normalized:
            matched_terms.append(term.term)
            if RISK_LEVEL_PRIORITY[term.risk_level] > RISK_LEVEL_PRIORITY[max_level]:
                max_level = term.risk_level
    return sorted(set(matched_terms)), max_level


def _match_rules(text: str, rules: list[MatchedRule]) -> list[MatchedRule]:
    normalized = text.lower()
    hits: list[MatchedRule] = []
    for rule in rules:
        if not rule.hit_terms:
            continue
        if all(term.lower() in normalized for term in rule.hit_terms):
            hits.append(rule)
    return sorted(
        hits,
        key=lambda item: (-RISK_LEVEL_PRIORITY[item.risk_level], item.priority, item.code),
    )


def _score_result(hit_rules: list[MatchedRule], term_level: str) -> tuple[str, int]:
    if hit_rules:
        risk_level = hit_rules[0].risk_level
        base_score = RISK_LEVEL_SCORE[risk_level]
        bonus = min(8, max(0, len(hit_rules) - 1) * 3)
        return risk_level, min(99, base_score + bonus)
    return term_level, RISK_LEVEL_SCORE[term_level]


def _build_reason(scene_label: str, hit_rules: list[MatchedRule], hit_terms: list[str], risk_level: str) -> str:
    if hit_rules:
        rule_names = "、".join(rule.name for rule in hit_rules[:3])
        terms = "、".join(hit_terms[:6]) if hit_terms else "无"
        return f"{scene_label}命中规则：{rule_names}；命中风险词：{terms}；综合判定为{risk_level}风险。"
    if hit_terms:
        return f"{scene_label}命中风险词：{'、'.join(hit_terms[:6])}；当前为基础词库识别，综合判定为{risk_level}风险。"
    return f"{scene_label}未命中已启用规则和词库，当前判定为低风险。"


def _build_suggestion(hit_rules: list[MatchedRule], risk_level: str) -> str:
    if hit_rules and hit_rules[0].suggestion_template:
        return hit_rules[0].suggestion_template
    if risk_level == "high":
        return "建议立即停止继续沟通或操作，联系子女或社区人员核实。"
    if risk_level == "medium":
        return "建议保持警惕，不要转账或泄露隐私信息，先联系熟人核实。"
    return "目前未发现明显高危特征，仍建议保持警惕，不点击陌生链接。"


def _audio_result_to_score(risk_level: str, confidence: float) -> int:
    base_score = RISK_LEVEL_SCORE[risk_level]
    if risk_level == "low":
        return min(49, max(10, int(base_score + confidence * 10)))
    if risk_level == "medium":
        return min(79, max(50, int(base_score + confidence * 10)))
    return min(99, max(80, int(base_score + confidence * 9)))


def _extract_json_object(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("模型输出中未找到 JSON 对象")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("模型输出 JSON 不是对象")
    return data


def _build_audio_fallback_result(reason: str) -> dict:
    return {
        "fraud_result": "疑似诈骗",
        "risk_level": "中",
        "has_fraud_evidence": False,
        "confidence": 0.0,
        "high_risk_behaviors": [],
        "evidence": [],
        "reason": f"模型分析失败，进入人工复核：{reason}",
        "suggestion": "记录但不通知家属",
    }


def _run_audio_guard_script(audio_path: str) -> dict:
    settings = get_settings()
    if not settings.audio_guard_enabled:
        return _build_audio_fallback_result("音频模型服务未启用")

    script_path = Path(settings.audio_guard_script_path)
    if not script_path.exists():
        return _build_audio_fallback_result(f"未找到推理脚本 {script_path}")
    if not os.access(script_path, os.X_OK):
        return _build_audio_fallback_result(f"推理脚本不可执行 {script_path}")

    try:
        completed = subprocess.run(
            [str(script_path), audio_path],
            capture_output=True,
            check=False,
            text=True,
            timeout=settings.audio_guard_timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return _build_audio_fallback_result("推理脚本执行超时")
    except Exception as exc:
        return _build_audio_fallback_result(str(exc))

    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()[-1:] or ["推理脚本执行失败"]
        return _build_audio_fallback_result(detail[0])

    try:
        return _extract_json_object(completed.stdout)
    except Exception as exc:
        return _build_audio_fallback_result(str(exc))


def _normalize_audio_result(model_result: dict) -> tuple[str, int, list[str], str, str, str]:
    fraud_result = str(model_result.get("fraud_result") or "疑似诈骗")
    risk_level = AUDIO_FRAUD_RESULT_TO_RISK_LEVEL.get(fraud_result, "medium")
    try:
        confidence = float(model_result.get("confidence", 0.0))
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    raw_behaviors = model_result.get("high_risk_behaviors")
    hit_terms = [str(item) for item in raw_behaviors] if isinstance(raw_behaviors, list) else []
    raw_evidence = model_result.get("evidence")
    evidence = [str(item) for item in raw_evidence] if isinstance(raw_evidence, list) else []
    reason = str(model_result.get("reason") or "模型未返回明确解释。")
    suggestion = str(model_result.get("suggestion") or _build_suggestion([], risk_level))
    evidence_detail = f"；关键证据：{'；'.join(evidence[:5])}" if evidence else ""
    reason_detail = f"音频模型判定：{fraud_result}；置信度：{confidence:.2f}；{reason}{evidence_detail}"
    return risk_level, _audio_result_to_score(risk_level, confidence), hit_terms, reason_detail, suggestion, fraud_result


def _get_family_receivers(session, elder_user_id: str) -> list[User]:
    family_ids = session.scalars(
        select(ElderFamilyBinding.family_user_id).where(
            ElderFamilyBinding.elder_user_id == elder_user_id,
            ElderFamilyBinding.status == "active",
        )
    ).all()
    if not family_ids:
        return []
    return session.execute(select(User).where(User.id.in_(family_ids))).scalars().all()


def _get_community_receiver(session) -> User | None:
    community_ids = session.scalars(
        select(UserRoleLink.user_id).join(User, User.id == UserRoleLink.user_id).where(UserRoleLink.role_id == "role-community")
    ).all()
    if not community_ids:
        return None
    return session.execute(select(User).where(User.id.in_(community_ids)).order_by(User.created_at.asc())).scalars().first()


def _create_alert_related_records(
    session,
    *,
    elder: User,
    source_type: str,
    source_record_id: str,
    risk_level: str,
    risk_score: int,
    reason_detail: str,
    suggestion_action: str,
    occurred_at: str,
    title: str,
    summary: str,
) -> tuple[RiskAlert | None, list[NotificationRecord], Workorder | None]:
    if risk_level not in {"medium", "high"}:
        return None, [], None

    alert = RiskAlert(
        elder_user_id=elder.id,
        source_type=source_type,
        source_record_id=source_record_id,
        risk_level=risk_level,
        risk_score=risk_score,
        title=title,
        summary=summary,
        reason_detail=reason_detail,
        suggestion_action=suggestion_action,
        status="pending_follow_up" if risk_level == "high" else "new",
        occurred_at=occurred_at,
    )
    session.add(alert)
    session.flush()

    notifications: list[NotificationRecord] = []
    for family_user in _get_family_receivers(session, elder.id):
        notification = NotificationRecord(
            alert_id=alert.id,
            receiver_user_id=family_user.id,
            channel="app",
            notification_type="risk_alert",
            title=f"{elder.display_name}出现{risk_level}风险告警",
            content=f"{elder.display_name}触发{title}，建议尽快联系核实。",
            status="sent",
            sent_at=occurred_at,
        )
        notifications.append(notification)
        session.add(notification)

    workorder = None
    if risk_level == "high":
        community_user = _get_community_receiver(session)
        if community_user:
            community_notification = NotificationRecord(
                alert_id=alert.id,
                receiver_user_id=community_user.id,
                channel="workbench",
                notification_type="community_dispatch",
                title=f"{elder.display_name}出现高风险告警",
                content=f"{elder.display_name}触发{title}，建议尽快电话回访或上门核实。",
                status="sent",
                sent_at=occurred_at,
            )
            notifications.append(community_notification)
            session.add(community_notification)
            workorder = Workorder(
                alert_id=alert.id,
                elder_user_id=elder.id,
                assigned_to_user_id=community_user.id,
                workorder_no=f"GD{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}{elder.id[-3:]}{alert.id[:6]}",
                title=f"{elder.display_name}{title}处置工单",
                priority="high",
                status="pending",
                dispose_method="phone_visit",
            )
            session.add(workorder)
            session.flush()
            session.add(
                WorkorderAction(
                    workorder_id=workorder.id,
                    operator_user_id=community_user.id,
                    action_type="create",
                    from_status=None,
                    to_status="pending",
                    note="高风险识别结果自动生成工单。",
                )
            )

    session.flush()
    return alert, notifications, workorder


def _analyze_text(scene: str, text: str) -> tuple[str, int, list[str], list[MatchedRule], str, str]:
    with session_scope() as session:
        lexicon_terms = _load_lexicon_terms(session, scene)
        rules = _load_rules(session, scene)
    hit_terms, term_level = _detect_terms(text, lexicon_terms)
    hit_rules = _match_rules(text, rules)
    risk_level, risk_score = _score_result(hit_rules, term_level)
    scene_label = "短信内容" if scene == "sms" else "通话文本"
    reason_detail = _build_reason(scene_label, hit_rules, hit_terms, risk_level)
    suggestion_action = _build_suggestion(hit_rules, risk_level)
    return risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action


def recognize_sms(*, elder_user_id: str, message_text: str, sender: str | None = None, occurred_at: str | None = None) -> dict:
    occurred_at = occurred_at or _now_iso()
    risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action = _analyze_text("sms", message_text)

    with session_scope() as session:
        elder = _ensure_elder_exists(session, elder_user_id)
        record = SmsRecognitionRecord(
            elder_user_id=elder_user_id,
            sender=sender,
            message_text=message_text,
            masked_message_text=message_text,
            risk_level=risk_level,
            risk_score=risk_score,
            hit_rule_codes=",".join(rule.code for rule in hit_rules),
            hit_terms=",".join(hit_terms),
            analysis_summary=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
        )
        session.add(record)
        session.flush()
        title = "疑似诈骗短信"
        summary = "短信命中诈骗关键词和规则，请谨慎处理。"
        alert, notifications, workorder = _create_alert_related_records(
            session,
            elder=elder,
            source_type="sms",
            source_record_id=record.id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason_detail=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
            title=title,
            summary=summary,
        )
        return {
            "scene": "sms",
            "record_id": record.id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "hit_rule_codes": [rule.code for rule in hit_rules],
            "hit_terms": hit_terms,
            "reason_detail": reason_detail,
            "suggestion_action": suggestion_action,
            "alert_id": alert.id if alert else None,
            "notification_ids": [item.id for item in notifications],
            "workorder_id": workorder.id if workorder else None,
        }


def recognize_call(
    *,
    elder_user_id: str,
    transcript_text: str,
    caller_number: str | None = None,
    duration_seconds: int | None = None,
    occurred_at: str | None = None,
) -> dict:
    occurred_at = occurred_at or _now_iso()
    risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action = _analyze_text("call", transcript_text)

    with session_scope() as session:
        elder = _ensure_elder_exists(session, elder_user_id)
        record = CallRecognitionRecord(
            elder_user_id=elder_user_id,
            caller_number=caller_number,
            transcript_text=transcript_text,
            transcript_summary=transcript_text[:200],
            duration_seconds=duration_seconds,
            risk_level=risk_level,
            risk_score=risk_score,
            hit_rule_codes=",".join(rule.code for rule in hit_rules),
            hit_terms=",".join(hit_terms),
            analysis_summary=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
        )
        session.add(record)
        session.flush()
        title = "疑似诈骗来电"
        summary = "通话文本命中诈骗话术和规则，请尽快核实。"
        alert, notifications, workorder = _create_alert_related_records(
            session,
            elder=elder,
            source_type="call",
            source_record_id=record.id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason_detail=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
            title=title,
            summary=summary,
        )
        return {
            "scene": "call",
            "record_id": record.id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "hit_rule_codes": [rule.code for rule in hit_rules],
            "hit_terms": hit_terms,
            "reason_detail": reason_detail,
            "suggestion_action": suggestion_action,
            "alert_id": alert.id if alert else None,
            "notification_ids": [item.id for item in notifications],
            "workorder_id": workorder.id if workorder else None,
        }


def recognize_call_audio(
    *,
    elder_user_id: str,
    audio_content: bytes,
    filename: str,
    call_session_id: str | None = None,
    caller_number: str | None = None,
    duration_seconds: int | None = None,
    occurred_at: str | None = None,
) -> dict:
    occurred_at = occurred_at or _now_iso()

    if duration_seconds is not None and duration_seconds < AUDIO_GUARD_MIN_DURATION_SECONDS:
        reason_detail = "通话时长不足 60 秒，按隐私最小化策略不上传模型分析，当前判定为低风险。"
        suggestion_action = "短通话已跳过云端分析，无需触发提醒。"
        with session_scope() as session:
            elder = _ensure_elder_exists(session, elder_user_id)
            record = CallRecognitionRecord(
                elder_user_id=elder.id,
                caller_number=caller_number,
                transcript_text=f"[call_session_id={call_session_id or 'unknown'}] 短通话未进行音频模型分析",
                transcript_summary="短通话未上传分析",
                duration_seconds=duration_seconds,
                risk_level="low",
                risk_score=RISK_LEVEL_SCORE["low"],
                hit_rule_codes="",
                hit_terms="",
                analysis_summary=reason_detail,
                suggestion_action=suggestion_action,
                occurred_at=occurred_at,
            )
            session.add(record)
            session.flush()
            return {
                "scene": "call_audio",
                "record_id": record.id,
                "risk_level": "low",
                "risk_score": RISK_LEVEL_SCORE["low"],
                "hit_rule_codes": [],
                "hit_terms": [],
                "reason_detail": reason_detail,
                "suggestion_action": suggestion_action,
                "alert_id": None,
                "notification_ids": [],
                "workorder_id": None,
            }

    suffix = Path(filename).suffix or ".webm"
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="guard-call-audio-") as temp_file:
            temp_file.write(audio_content)
            temp_path = temp_file.name
        model_result = _run_audio_guard_script(temp_path)
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass

    risk_level, risk_score, hit_terms, reason_detail, suggestion_action, fraud_result = _normalize_audio_result(model_result)

    with session_scope() as session:
        elder = _ensure_elder_exists(session, elder_user_id)
        record = CallRecognitionRecord(
            elder_user_id=elder.id,
            caller_number=caller_number,
            transcript_text=f"[call_session_id={call_session_id or 'unknown'}] 音频模型分析结果：{fraud_result}",
            transcript_summary=reason_detail[:200],
            duration_seconds=duration_seconds,
            risk_level=risk_level,
            risk_score=risk_score,
            hit_rule_codes=AUDIO_GUARD_RULE_CODE,
            hit_terms=",".join(hit_terms),
            analysis_summary=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
        )
        session.add(record)
        session.flush()
        alert, notifications, workorder = _create_alert_related_records(
            session,
            elder=elder,
            source_type="call",
            source_record_id=record.id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason_detail=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
            title="AI通话反诈分析",
            summary=f"通话录音经 AI 模型判定为{fraud_result}，请及时核实。",
        )
        return {
            "scene": "call_audio",
            "record_id": record.id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "hit_rule_codes": [AUDIO_GUARD_RULE_CODE],
            "hit_terms": hit_terms,
            "reason_detail": reason_detail,
            "suggestion_action": suggestion_action,
            "alert_id": alert.id if alert else None,
            "notification_ids": [item.id for item in notifications],
            "workorder_id": workorder.id if workorder else None,
        }
