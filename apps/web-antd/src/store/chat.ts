import type {
  CallSessionItem,
  ChatConversationDetail,
  ChatConversationItem,
  ChatMessageItem,
  ChatRecommendedContactItem,
  ChatUserSearchItem,
  OnlineStateItem,
} from '#/api';

import { computed, ref } from 'vue';

import { useAppConfig } from '@vben/hooks';
import { useAccessStore, useUserStore } from '@vben/stores';

import { message } from 'ant-design-vue';
import { defineStore } from 'pinia';

import {
  createCallSessionApi,
  createChatConversationApi,
  endCallSessionApi,
  getCallSessionDetailApi,
  getCallHistoryApi,
  getChatConversationDetailApi,
  getChatConversationListApi,
  getChatOnlineStatesApi,
  getChatRecommendedContactsApi,
  getChatUnreadSummaryApi,
  markChatReadApi,
  searchChatUsersApi,
  sendCallSignalApi,
  sendChatMessageApi,
  uploadCallAudioRecognitionApi,
} from '#/api';

const { apiURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

function buildChatWsUrl(token: string) {
  const url = new URL(apiURL, window.location.origin);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.pathname = `${url.pathname.replace(/\/$/, '')}/chats/ws`;
  url.searchParams.set('token', token);
  return url.toString();
}

function buildCallEndUrl(callSessionId: string) {
  const url = new URL(apiURL, window.location.origin);
  url.pathname = `${url.pathname.replace(/\/$/, '')}/chats/calls/${callSessionId}/end`;
  return url.toString();
}

function buildChatApiUrl(path: string) {
  const url = new URL(apiURL, window.location.origin);
  url.pathname = `${url.pathname.replace(/\/$/, '')}${path}`;
  return url.toString();
}

type CallPhase =
  | 'accepting'
  | 'calling'
  | 'connected'
  | 'ended'
  | 'idle'
  | 'incoming'
  | 'reconnecting';

type JwtPayload = {
  sub?: string;
};

export const useChatStore = defineStore('chat', () => {
  const accessStore = useAccessStore();
  const userStore = useUserStore();

  const conversations = ref<ChatConversationItem[]>([]);
  const currentConversation = ref<ChatConversationDetail | null>(null);
  const recommendedContacts = ref<ChatRecommendedContactItem[]>([]);
  const searchResults = ref<ChatUserSearchItem[]>([]);
  const totalUnread = ref(0);
  const onlineStates = ref<Record<string, OnlineStateItem>>({});
  const typingText = ref('');
  const sending = ref(false);
  const connecting = ref(false);
  const socket = ref<null | WebSocket>(null);
  const callHistory = ref<CallSessionItem[]>([]);
  const activeCall = ref<CallSessionItem | null>(null);
  const callPhase = ref<CallPhase>('idle');
  const callError = ref('');
  const localAudioEnabled = ref(true);
  const localVideoEnabled = ref(false);
  const permissionState = ref<'denied' | 'granted' | 'idle'>('idle');
  const localStream = ref<MediaStream | null>(null);
  const remoteStream = ref<MediaStream | null>(null);
  const peerConnection = ref<null | RTCPeerConnection>(null);
  const callSeconds = ref(0);
  let callTimer: null | ReturnType<typeof setInterval> = null;
  let heartbeatTimer: null | ReturnType<typeof setInterval> = null;
  let reconnectTimer: null | ReturnType<typeof setTimeout> = null;
  let manualDisconnect = false;
  let syncingActiveCall = false;
  let lastUnloadCleanupCallId = '';
  let endingCallId = '';
  let callRecorder: MediaRecorder | null = null;
  let callRecorderStartedAt = 0;
  let callRecordChunks: Blob[] = [];
  let callRecordAudioContext: AudioContext | null = null;
  let callRecordStream: MediaStream | null = null;
  let callRecordingNote = '';

  const rtcConfig = computed(() => {
    const stunServers = (
      import.meta.env.VITE_CALL_STUN_SERVERS || 'stun:stun.l.google.com:19302'
    )
      .split(',')
      .map((item: string) => item.trim())
      .filter(Boolean);
    const iceServers: RTCIceServer[] = stunServers.length > 0
      ? [{ urls: stunServers }]
      : [];
    if (import.meta.env.VITE_CALL_TURN_URL) {
      iceServers.push({
        urls: import.meta.env.VITE_CALL_TURN_URL,
        username: import.meta.env.VITE_CALL_TURN_USERNAME,
        credential: import.meta.env.VITE_CALL_TURN_PASSWORD,
      });
    }
    return { iceServers };
  });

  async function loadConversations() {
    const [conversationRows, unreadSummary, recommendations] = await Promise.all([
      getChatConversationListApi(),
      getChatUnreadSummaryApi(),
      getChatRecommendedContactsApi(),
    ]);
    conversations.value = conversationRows;
    totalUnread.value = unreadSummary.total_unread;
    recommendedContacts.value = recommendations;
    await refreshOnlineStates();
  }

  function decodeJwtPayload(token: null | string) {
    if (!token) return null;
    try {
      const [, payload = ''] = token.split('.');
      if (!payload) return null;
      const normalized = payload
        .replace(/-/g, '+')
        .replace(/_/g, '/')
        .padEnd(Math.ceil(payload.length / 4) * 4, '=');
      return JSON.parse(window.atob(normalized)) as JwtPayload;
    } catch {
      return null;
    }
  }

  function getCurrentUserId() {
    return userStore.userInfo?.userId || decodeJwtPayload(accessStore.accessToken)?.sub || '';
  }

  function isCurrentUserElder() {
    return userStore.userInfo?.roles?.includes('elder') ?? false;
  }

  function isCurrentUserParticipant(call: CallSessionItem) {
    const selfId = getCurrentUserId();
    return !!selfId && [call.initiator_user_id, call.receiver_user_id].includes(selfId);
  }

  function isCurrentUserReceiver(call: CallSessionItem) {
    const selfId = getCurrentUserId();
    return isCurrentUserParticipant(call) && call.initiator_user_id !== selfId;
  }

  async function ensureCallEventPayload(
    call: CallSessionItem,
    eventType: 'call.answer' | 'call.ice-candidate' | 'call.offer',
  ) {
    if (call.events.some((item) => item.event_type === eventType)) {
      return call;
    }
    const refreshed = await getCallSessionDetailApi(call.id);
    activeCall.value = refreshed;
    return refreshed;
  }

  async function searchUsers(keyword: string) {
    searchResults.value = keyword ? await searchChatUsersApi(keyword) : [];
  }

  async function openConversation(conversationId: string) {
    currentConversation.value = await getChatConversationDetailApi(conversationId);
    callHistory.value = await getCallHistoryApi(conversationId);
    const lastMessage = currentConversation.value.messages.at(-1);
    if (lastMessage && !lastMessage.is_self) {
      const summary = await markChatReadApi(conversationId, lastMessage.id);
      totalUnread.value = summary.total_unread;
    }
  }

  async function startConversation(userId: string) {
    const detail = await createChatConversationApi(userId);
    currentConversation.value = detail;
    callHistory.value = await getCallHistoryApi(detail.id);
    await loadConversations();
  }

  async function sendMessage(content: string) {
    if (!currentConversation.value || !content.trim()) return;
    sending.value = true;
    try {
      const messageRow = await sendChatMessageApi(currentConversation.value.id, content);
      mergeMessage(messageRow);
      await loadConversations();
    } finally {
      sending.value = false;
    }
  }

  function mergeMessage(messageRow: ChatMessageItem) {
    if (currentConversation.value?.id !== messageRow.conversation_id) return;
    const exists = currentConversation.value.messages.some((item) => item.id === messageRow.id);
    if (!exists) {
      currentConversation.value.messages.push(messageRow);
    }
  }

  async function refreshOnlineStates() {
    const ids = conversations.value
      .map((item) => item.peer_user_id)
      .filter(
        (item): item is string => typeof item === 'string' && item.length > 0,
      );
    if (ids.length === 0) return;
    const rows = await getChatOnlineStatesApi(ids);
    onlineStates.value = Object.fromEntries(rows.map((item) => [item.user_id, item]));
  }

  function hasMediaSession() {
    return !!peerConnection.value || !!localStream.value || !!remoteStream.value;
  }

  function isLiveCallStatus(status: string) {
    return ['accepted', 'initiated', 'ringing'].includes(status);
  }

  function isCallInProgress() {
    return ['accepting', 'calling', 'connected', 'incoming', 'reconnecting'].includes(
      callPhase.value,
    );
  }

  function resetCallTimer() {
    if (callTimer) clearInterval(callTimer);
    callTimer = null;
    callSeconds.value = 0;
  }

  function getRecorderMimeType() {
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
    ];
    return candidates.find((item) => MediaRecorder.isTypeSupported(item)) || '';
  }

  function cleanupCallRecorderResources() {
    callRecordAudioContext?.close().catch(() => {});
    callRecordAudioContext = null;
    callRecordStream?.getTracks().forEach((track) => track.stop());
    callRecordStream = null;
  }

  function startCallRecording() {
    if (callRecorder || !isCurrentUserElder()) return;
    if (!window.MediaRecorder || !localStream.value) return;

    try {
      const AudioContextCtor = window.AudioContext || (window as any).webkitAudioContext;
      const audioContext = new AudioContextCtor() as AudioContext;
      const destination = audioContext.createMediaStreamDestination();
      let mixedTracks = 0;

      if (localStream.value.getAudioTracks().length > 0) {
        audioContext.createMediaStreamSource(localStream.value).connect(destination);
        mixedTracks += 1;
      }

      if (remoteStream.value?.getAudioTracks().length) {
        audioContext.createMediaStreamSource(remoteStream.value).connect(destination);
        mixedTracks += 1;
      } else {
        callRecordingNote = '远端音轨尚未就绪，本次录音仅包含本地音频。';
      }

      if (mixedTracks === 0) {
        void audioContext.close();
        return;
      }

      const mimeType = getRecorderMimeType();
      callRecordAudioContext = audioContext;
      callRecordStream = destination.stream;
      callRecordChunks = [];
      callRecorder = new MediaRecorder(
        destination.stream,
        mimeType ? { mimeType } : undefined,
      );
      callRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          callRecordChunks.push(event.data);
        }
      };
      callRecorderStartedAt = Date.now();
      callRecorder.start(1000);
    } catch {
      callRecorder = null;
      callRecordChunks = [];
      cleanupCallRecorderResources();
    }
  }

  function stopCallRecording() {
    return new Promise<Blob | null>((resolve) => {
      const recorder = callRecorder;
      if (!recorder) {
        cleanupCallRecorderResources();
        resolve(null);
        return;
      }
      const mimeType = recorder.mimeType || 'audio/webm';
      const finish = () => {
        const blob = callRecordChunks.length > 0
          ? new Blob(callRecordChunks, { type: mimeType })
          : null;
        callRecorder = null;
        callRecorderStartedAt = 0;
        callRecordChunks = [];
        cleanupCallRecorderResources();
        resolve(blob);
      };
      recorder.onstop = finish;
      if (recorder.state === 'inactive') {
        finish();
      } else {
        recorder.stop();
      }
    });
  }

  async function uploadCallRecording(
    blob: Blob | null,
    call: CallSessionItem | null,
    durationSeconds: number,
  ) {
    if (!blob || !call || !isCurrentUserElder()) {
      callRecordingNote = '';
      return;
    }
    if (durationSeconds < 60) {
      message.info('短通话未上传分析，已按隐私策略丢弃录音。');
      callRecordingNote = '';
      return;
    }
    try {
      const result = await uploadCallAudioRecognitionApi({
        audioFile: blob,
        callSessionId: call.id,
        durationSeconds,
        elderUserId: getCurrentUserId(),
        filename: `call-${call.id}.webm`,
      });
      if (result.risk_level === 'high') {
        message.error('通话录音已分析：高风险，已通知守护人。');
      } else if (result.risk_level === 'medium') {
        message.warning('通话录音已分析：疑似风险，已生成提醒。');
      } else {
        message.success('通话录音已分析：暂未发现明显风险。');
      }
      if (callRecordingNote) {
        message.info(callRecordingNote);
      }
    } catch {
      message.warning('录音分析失败，通话已正常结束。');
    } finally {
      callRecordingNote = '';
    }
  }

  function markCallConnected(answeredAt?: null | string) {
    callPhase.value = 'connected';
    startCallTimer(answeredAt);
    startCallRecording();
  }

  function upsertOnlineState(state: OnlineStateItem) {
    onlineStates.value = {
      ...onlineStates.value,
      [state.user_id]: state,
    };
  }

  function clearHeartbeatTimer() {
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }

  function startHeartbeat(ws: WebSocket) {
    clearHeartbeatTimer();
    heartbeatTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ event: 'ping' }));
      }
    }, 25_000);
  }

  function clearReconnectTimer() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  function clearMediaResources() {
    peerConnection.value?.close();
    peerConnection.value = null;
    localStream.value?.getTracks().forEach((track) => track.stop());
    remoteStream.value?.getTracks().forEach((track) => track.stop());
    localStream.value = null;
    remoteStream.value = null;
  }

  function resetActiveCallState() {
    void stopCallRecording();
    clearMediaResources();
    resetCallTimer();
    activeCall.value = null;
    callPhase.value = 'idle';
    lastUnloadCleanupCallId = '';
    endingCallId = '';
    callRecorderStartedAt = 0;
    callRecordingNote = '';
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connectWs();
    }, 2000);
  }

  function startCallTimer(answeredAt?: null | string) {
    resetCallTimer();
    const base = answeredAt ? new Date(answeredAt).getTime() : Date.now();
    callTimer = setInterval(() => {
      callSeconds.value = Math.max(Math.floor((Date.now() - base) / 1000), 0);
    }, 1000);
  }

  async function ensureLocalStream(withVideo: boolean) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: withVideo,
      });
      permissionState.value = 'granted';
      localStream.value?.getTracks().forEach((track) => track.stop());
      localStream.value = stream;
      localAudioEnabled.value = true;
      localVideoEnabled.value = withVideo;
      return stream;
    } catch (error) {
      permissionState.value = 'denied';
      callError.value = '未获取到麦克风/摄像头权限，请检查浏览器设置。';
      throw error;
    }
  }

  function createPeerConnection() {
    if (peerConnection.value) {
      peerConnection.value.close();
    }
    const pc = new RTCPeerConnection(rtcConfig.value);
    const remote = new MediaStream();
    remoteStream.value = remote;
    pc.ontrack = (event) => {
      event.streams[0]?.getTracks().forEach((track) => remote.addTrack(track));
    };
    pc.onicecandidate = (event) => {
      if (event.candidate && activeCall.value) {
        void sendSignal('call.ice-candidate', {
          call_session_id: activeCall.value.id,
          candidate: event.candidate.toJSON(),
        });
      }
    };
    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'connected') {
        markCallConnected(activeCall.value?.answered_at);
      }
      if (['disconnected', 'failed'].includes(pc.connectionState)) {
        callPhase.value = 'reconnecting';
      }
    };
    peerConnection.value = pc;
    return pc;
  }

  async function preparePeer(withVideo: boolean) {
    const stream = await ensureLocalStream(withVideo);
    const pc = createPeerConnection();
    stream.getTracks().forEach((track) => pc.addTrack(track, stream));
    return pc;
  }

  async function requestChatApi<T>(
    path: string,
    init: RequestInit = {},
    timeoutMs = 4000,
  ) {
    const token = accessStore.accessToken;
    if (!token) {
      return null;
    }
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(buildChatApiUrl(path), {
        ...init,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...(init.headers || {}),
        },
        signal: controller.signal,
      });
      if (!response.ok) {
        return null;
      }
      const payload = await response.json();
      return (payload?.data ?? null) as null | T;
    } catch {
      return null;
    } finally {
      clearTimeout(timer);
    }
  }

  async function syncActiveCallState() {
    if (syncingActiveCall) {
      return;
    }
    syncingActiveCall = true;
    try {
      const calls = await requestChatApi<CallSessionItem[]>('/chats/calls');
      if (!calls) {
        return;
      }
      const liveCall = calls.find((item) => isLiveCallStatus(item.status));
      if (!liveCall) {
        if (!hasMediaSession() && !isCallInProgress()) {
          activeCall.value = null;
          callPhase.value = 'idle';
        }
        return;
      }
      if (liveCall.status === 'accepted' && !hasMediaSession()) {
        await requestChatApi(`/chats/calls/${liveCall.id}/end`, {
          method: 'POST',
          body: JSON.stringify({ reason: 'failed' }),
        });
        resetActiveCallState();
        callError.value = '';
        return;
      }
      if (!hasMediaSession()) {
        hydrateCallState(liveCall);
      }
    } finally {
      syncingActiveCall = false;
    }
  }

  async function startCall(callType: 'audio' | 'video') {
    if (!currentConversation.value) return;
    if (activeCall.value && ['calling', 'connected', 'incoming'].includes(callPhase.value)) {
      message.warning('当前已有进行中的通话，请先结束后再试。');
      return;
    }
    callError.value = '';
    callPhase.value = 'calling';
    try {
      const call = await createCallSessionApi(currentConversation.value.id, callType);
      activeCall.value = call;
      await preparePeer(callType === 'video');
      const offer = await peerConnection.value!.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: callType === 'video',
      });
      await peerConnection.value!.setLocalDescription(offer);
      await sendSignal('call.offer', {
        call_session_id: call.id,
        type: offer.type,
        sdp: offer.sdp,
      });
      await loadConversations();
    } catch (error: any) {
      resetActiveCallState();
      callError.value = error?.message || '发起通话失败，请稍后重试。';
    }
  }

  async function sendSignal(
    event:
      | 'call.accept'
      | 'call.answer'
      | 'call.busy'
      | 'call.end'
      | 'call.ice-candidate'
      | 'call.offer'
      | 'call.reject'
      | 'call.ringing'
      | 'call.timeout',
    data?: Record<string, any>,
  ) {
    if (!activeCall.value) return;
    await sendCallSignalApi(event, activeCall.value.id, data);
  }

  async function acceptIncomingCall() {
    if (!activeCall.value) return;
    callError.value = '';
    callPhase.value = 'accepting';
    const withVideo = activeCall.value.call_type === 'video';
    await preparePeer(withVideo);
    let latestCall = activeCall.value;
    let offerPayload = latestCall.events
      .findLast((item) => item.event_type === 'call.offer')?.payload_json;
    if (!offerPayload?.sdp) {
      for (let attempt = 0; attempt < 3; attempt += 1) {
        latestCall = await getCallSessionDetailApi(latestCall.id);
        activeCall.value = latestCall;
        offerPayload = latestCall.events
          .findLast((item) => item.event_type === 'call.offer')?.payload_json;
        if (offerPayload?.sdp) break;
        await new Promise((resolve) => window.setTimeout(resolve, 250));
      }
    }
    if (!offerPayload?.sdp) {
      callPhase.value = 'incoming';
      callError.value = '主叫端邀请尚未准备完成，请稍后再试。';
      return;
    }
    if (offerPayload?.sdp) {
      await peerConnection.value!.setRemoteDescription(
        new RTCSessionDescription({
          type: 'offer',
          sdp: offerPayload.sdp,
        }),
      );
    }
    await sendSignal('call.accept', {
      call_session_id: activeCall.value.id,
    });
    const answer = await peerConnection.value!.createAnswer();
    await peerConnection.value!.setLocalDescription(answer);
    await sendSignal('call.answer', {
      call_session_id: activeCall.value.id,
      type: answer.type,
      sdp: answer.sdp,
    });
    markCallConnected();
  }

  async function rejectIncomingCall(reason: 'busy' | 'rejected' = 'rejected') {
    if (!activeCall.value) return;
    await sendSignal(reason === 'busy' ? 'call.busy' : 'call.reject', {
      call_session_id: activeCall.value.id,
    });
    await endCurrentCall(reason);
  }

  async function endCurrentCall(
    reason: 'busy' | 'cancelled' | 'ended' | 'failed' | 'rejected' | 'timeout' = 'ended',
    options: { notifyServer?: boolean } = {},
  ) {
    const callId = activeCall.value?.id;
    const callSnapshot = activeCall.value;
    const durationSnapshot = Math.max(
      callSeconds.value,
      callRecorderStartedAt > 0
        ? Math.floor((Date.now() - callRecorderStartedAt) / 1000)
        : 0,
    );
    if (callId && endingCallId === callId) {
      return;
    }
    if (callId) {
      endingCallId = callId;
      if (options.notifyServer !== false) {
        try {
          await endCallSessionApi(callId, reason);
        } catch {}
      }
    }
    const recordingBlob = await stopCallRecording();
    clearMediaResources();
    callPhase.value = 'ended';
    setTimeout(() => {
      callPhase.value = 'idle';
      activeCall.value = null;
      if (endingCallId === callId) {
        endingCallId = '';
      }
    }, 1200);
    resetCallTimer();
    if (currentConversation.value) {
      currentConversation.value = await getChatConversationDetailApi(currentConversation.value.id);
      callHistory.value = await getCallHistoryApi(currentConversation.value.id);
      await loadConversations();
    }
    if (!callId) {
      endingCallId = '';
    }
    void uploadCallRecording(recordingBlob, callSnapshot, durationSnapshot);
  }

  function flushActiveCallOnUnload(reason: 'ended' | 'failed' = 'failed') {
    const callId = activeCall.value?.id;
    const token = accessStore.accessToken;
    if (!callId || !token || !isCallInProgress()) {
      return;
    }
    if (lastUnloadCleanupCallId === callId) {
      return;
    }
    lastUnloadCleanupCallId = callId;
    void fetch(buildCallEndUrl(callId), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reason }),
      keepalive: true,
    }).catch(() => {});
  }

  function toggleAudio() {
    const enabled = !localAudioEnabled.value;
    localStream.value?.getAudioTracks().forEach((track) => {
      track.enabled = enabled;
    });
    localAudioEnabled.value = enabled;
  }

  async function toggleVideo() {
    if (!activeCall.value) return;
    if (localVideoEnabled.value) {
      localStream.value?.getVideoTracks().forEach((track) => {
        track.enabled = false;
        track.stop();
      });
      localVideoEnabled.value = false;
      return;
    }
    const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
    const videoTrack = videoStream.getVideoTracks()[0];
    if (!videoTrack || !peerConnection.value) return;
    const sender = peerConnection.value
      .getSenders()
      .find((item) => item.track?.kind === 'video');
    if (sender) {
      await sender.replaceTrack(videoTrack);
    } else if (localStream.value) {
      localStream.value.addTrack(videoTrack);
      peerConnection.value.addTrack(videoTrack, localStream.value);
    }
    localVideoEnabled.value = true;
  }

  function hydrateCallState(call: CallSessionItem) {
    activeCall.value = call;
    if (call.status === 'accepted') {
      markCallConnected(call.answered_at);
    } else if (
      isCurrentUserReceiver(call) &&
      ['initiated', 'ringing'].includes(call.status)
    ) {
      callPhase.value = 'incoming';
    } else if (['initiated', 'ringing'].includes(call.status)) {
      callPhase.value = 'calling';
    } else if (['busy', 'failed', 'missed', 'rejected'].includes(call.status)) {
      callPhase.value = 'ended';
    }
  }

  async function handleCallEvent(event: string, payload: CallSessionItem) {
    let nextPayload = payload;
    if (
      event === 'call.answer' ||
      event === 'call.ice-candidate' ||
      event === 'call.offer'
    ) {
      nextPayload = await ensureCallEventPayload(nextPayload, event);
    }
    hydrateCallState(nextPayload);
    if (event === 'call.invite' && isCurrentUserReceiver(nextPayload)) {
      message.info(`${currentConversation.value?.peer_name || '对方'} 发起了${payload.call_type === 'video' ? '视频' : '语音'}通话`);
    }
    if (event === 'call.offer' && isCurrentUserReceiver(nextPayload)) {
      callPhase.value = 'incoming';
    }
    if (event === 'call.answer') {
      const answerPayload = nextPayload.events
        .findLast((item) => item.event_type === 'call.answer')?.payload_json;
      if (answerPayload?.sdp && peerConnection.value) {
        await peerConnection.value.setRemoteDescription(
          new RTCSessionDescription({
            type: 'answer',
            sdp: answerPayload.sdp,
          }),
        );
      }
      markCallConnected(nextPayload.answered_at);
    }
    if (event === 'call.ice-candidate') {
      const candidatePayload = nextPayload.events
        .findLast((item) => item.event_type === 'call.ice-candidate')?.payload_json;
      const candidate = candidatePayload?.candidate;
      if (candidate && peerConnection.value) {
        await peerConnection.value.addIceCandidate(new RTCIceCandidate(candidate));
      }
    }
    if (['call.busy', 'call.end', 'call.reject', 'call.timeout'].includes(event)) {
      const endReasonMap = {
        'call.busy': 'busy',
        'call.end': 'ended',
        'call.reject': 'rejected',
        'call.timeout': 'timeout',
      } as const;
      await endCurrentCall(
        endReasonMap[event as keyof typeof endReasonMap],
        { notifyServer: false },
      );
    }
  }

  function connectWs() {
    const token = accessStore.accessToken;
    if (!token || socket.value || connecting.value) return;
    manualDisconnect = false;
    connecting.value = true;
    const ws = new WebSocket(buildChatWsUrl(token));
    ws.addEventListener('open', () => {
      clearReconnectTimer();
      connecting.value = false;
      socket.value = ws;
      startHeartbeat(ws);
      ws.send(JSON.stringify({ event: 'ping' }));
      void refreshOnlineStates();
      void syncActiveCallState();
    });
    ws.addEventListener('message', async (event) => {
      const payload = JSON.parse(event.data);
      if (payload.event === 'connected') {
        await refreshOnlineStates();
      }
      if (payload.event === 'presence') {
        upsertOnlineState(payload.data as OnlineStateItem);
      }
      if (payload.event === 'message') {
        mergeMessage(payload.data as ChatMessageItem);
        await loadConversations();
      }
      if (payload.event === 'typing' && payload.data.user_id !== getCurrentUserId()) {
        typingText.value = `${payload.data.display_name} 正在输入...`;
        setTimeout(() => {
          typingText.value = '';
        }, 1500);
      }
      if (payload.event === 'read' && currentConversation.value) {
        currentConversation.value.messages = currentConversation.value.messages.map((item) =>
          item.id === payload.data.last_read_message_id
            ? { ...item, read_by_all_at: new Date().toISOString() }
            : item,
        );
        totalUnread.value = payload.data.total_unread ?? totalUnread.value;
      }
      if (typeof payload.event === 'string' && payload.event.startsWith('call.')) {
        await handleCallEvent(payload.event, payload.data as CallSessionItem);
      }
    });
    ws.addEventListener('error', () => {
      ws.close();
    });
    ws.addEventListener('close', () => {
      clearHeartbeatTimer();
      if (socket.value === ws) {
        socket.value = null;
      }
      connecting.value = false;
      if (manualDisconnect) return;
      scheduleReconnect();
    });
  }

  function disconnectWs() {
    manualDisconnect = true;
    clearReconnectTimer();
    clearHeartbeatTimer();
    connecting.value = false;
    const ws = socket.value;
    socket.value = null;
    if (
      ws &&
      (ws.readyState === WebSocket.CONNECTING ||
        ws.readyState === WebSocket.OPEN)
    ) {
      ws.close();
    }
  }

  function $reset() {
    disconnectWs();
    resetActiveCallState();
    conversations.value = [];
    currentConversation.value = null;
    recommendedContacts.value = [];
    searchResults.value = [];
    totalUnread.value = 0;
    onlineStates.value = {};
    typingText.value = '';
    sending.value = false;
    callHistory.value = [];
    activeCall.value = null;
    callError.value = '';
    localAudioEnabled.value = true;
    localVideoEnabled.value = false;
    permissionState.value = 'idle';
  }

  function sendTyping() {
    if (!socket.value || !currentConversation.value) return;
    socket.value.send(
      JSON.stringify({
        event: 'typing',
        data: {
          conversation_id: currentConversation.value.id,
        },
      }),
    );
  }

  return {
    $reset,
    acceptIncomingCall,
    activeCall,
    callError,
    callHistory,
    callPhase,
    callSeconds,
    connectWs,
    connecting,
    conversations,
    currentConversation,
    disconnectWs,
    endCurrentCall,
    flushActiveCallOnUnload,
    loadConversations,
    localAudioEnabled,
    localStream,
    localVideoEnabled,
    onlineStates,
    openConversation,
    permissionState,
    recommendedContacts,
    refreshOnlineStates,
    rejectIncomingCall,
    remoteStream,
    searchResults,
    searchUsers,
    sendMessage,
    sendTyping,
    sending,
    socket,
    startCall,
    startConversation,
    toggleAudio,
    toggleVideo,
    totalUnread,
    typingText,
  };
});
