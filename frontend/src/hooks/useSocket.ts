/**
 * Socket.IO hook for real-time communication with the FastAPI backend.
 * Handles connection lifecycle, session management, and step-by-step updates.
 */

import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useSimStore } from '../store/useSimStore';
import type { StateSnapshot } from '../types/quantum';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const {
    setConnectionStatus,
    setSessionId,
    setStateHistory,
    setCurrentStep,
  } = useSimStore();

  useEffect(() => {
    const socket = io(API_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      setConnectionStatus('connected');
    });

    socket.on('disconnect', () => {
      setConnectionStatus('disconnected');
    });

    socket.on('connect_error', () => {
      setConnectionStatus('error');
    });

    socket.on('session_started', (data: {
      session_id: string;
      total_steps: number;
      current_step: number;
      state: StateSnapshot;
    }) => {
      setSessionId(data.session_id);
    });

    socket.on('step_update', (data: {
      session_id: string;
      current_step: number;
      total_steps: number;
      state: StateSnapshot;
      step_label: string;
      is_first: boolean;
      is_last: boolean;
    }) => {
      setCurrentStep(data.current_step);
    });

    socket.on('error', (data: { error: string }) => {
      console.error('[Socket.IO] Error:', data.error);
    });

    return () => {
      socket.disconnect();
    };
  }, [setConnectionStatus, setSessionId, setStateHistory, setCurrentStep]);

  const startSession = useCallback((data: Record<string, unknown>) => {
    socketRef.current?.emit('start_session', data);
  }, []);

  const sendStep = useCallback((sessionId: string, action: string, step?: number) => {
    socketRef.current?.emit('step', { session_id: sessionId, action, step });
  }, []);

  return { startSession, sendStep, socket: socketRef };
}
