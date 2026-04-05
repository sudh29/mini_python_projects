/**
 * WebSocket hook for real-time bot status updates.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { WSMessage } from '../types';
import { getAuthToken } from '../services/api';

interface UseWebSocketOptions {
  onMessage?: (message: WSMessage) => void;
  onStatusUpdate?: (botId: string, status: string, runId?: string) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onStatusUpdate,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const token = getAuthToken() || '';
    const wsBase = (import.meta.env.VITE_API_BASE || 'http://localhost:8000')
      .replace('http', 'ws');
    const url = `${wsBase}/ws/status?token=${token}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (mountedRef.current) {
          setIsConnected(true);
          console.log('[WS] Connected');
        }
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const msg: WSMessage = JSON.parse(event.data);
          setLastMessage(msg);
          onMessage?.(msg);

          if (msg.type === 'status_update' && msg.bot_id && msg.status) {
            onStatusUpdate?.(msg.bot_id, msg.status, msg.run_id);
          }
        } catch {
          // Ignore non-JSON messages (e.g., "pong")
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setIsConnected(false);
        console.log('[WS] Disconnected');
        if (autoReconnect) {
          reconnectTimerRef.current = setTimeout(connect, reconnectInterval);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      if (autoReconnect && mountedRef.current) {
        reconnectTimerRef.current = setTimeout(connect, reconnectInterval);
      }
    }
  }, [onMessage, onStatusUpdate, autoReconnect, reconnectInterval]);

  // Send a message through the WebSocket
  const send = useCallback((data: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    // Keepalive ping every 25s
    const pingInterval = setInterval(() => {
      send('ping');
    }, 25000);

    return () => {
      mountedRef.current = false;
      clearInterval(pingInterval);
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect, send]);

  return { isConnected, lastMessage, send };
}
