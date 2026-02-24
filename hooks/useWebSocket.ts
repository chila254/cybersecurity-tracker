"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface WebSocketMessage {
  type: string;
  entity?: string;
  incident_id?: number;
  vulnerability_id?: number;
  title?: string;
  severity?: string;
  data?: any;
  timestamp?: string;
}

interface UseWebSocketOptions {
  url: string;
  token?: string;
  enabled?: boolean;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export function useWebSocket({
  url,
  token,
  enabled = true,
  onMessage,
  onError,
  onClose,
  reconnectAttempts = 5,
  reconnectDelay = 3000,
}: UseWebSocketOptions) {
  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const connect = useCallback(() => {
    if (!enabled || !token) return;

    try {
      const wsUrl = `${url}?token=${token}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log("✅ WebSocket connected");
        setIsConnected(true);
        reconnectCount.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log("📨 WebSocket message:", message);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.current.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        setIsConnected(false);
        onError?.(error);
      };

      ws.current.onclose = () => {
        console.log("🔌 WebSocket disconnected");
        setIsConnected(false);
        onClose?.();

        // Attempt to reconnect
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current += 1;
          const delay = reconnectDelay * Math.pow(2, reconnectCount.current - 1); // Exponential backoff
          console.log(
            `🔄 Reconnecting in ${delay}ms (attempt ${reconnectCount.current}/${reconnectAttempts})`
          );
          setTimeout(connect, delay);
        } else {
          console.error("❌ Failed to reconnect after multiple attempts");
        }
      };
    } catch (error) {
      console.error("Error creating WebSocket:", error);
      setIsConnected(false);
    }
  }, [url, token, enabled, onMessage, onError, onClose, reconnectAttempts, reconnectDelay]);

  useEffect(() => {
    if (enabled && token) {
      connect();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [enabled, token, connect]);

  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket is not connected");
    }
  }, []);

  const ping = useCallback(() => {
    sendMessage({ type: "ping" });
  }, [sendMessage]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    ping,
    reconnectCount: reconnectCount.current,
  };
}
