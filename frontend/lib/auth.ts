"use client";
// Session = token + user, kept in memory and in this tab's sessionStorage (so a refresh keeps you
// logged in, and a customer tab and a broker tab can be open side by side for the demo).
import { useSyncExternalStore } from "react";
import type { AuthResponse, Role, User } from "./types";

export type Session =
  | { status: "loading" }
  | { status: "anon" }
  | { status: "authed"; token: string; user: User; isNew: boolean };

const KEY = "aqarai-session";
const LOADING: Session = { status: "loading" };
const ANON: Session = { status: "anon" };
const listeners = new Set<() => void>();

let raw: string | null | undefined; // undefined = not read yet
let snapshot: Session = LOADING;

function read(): Session {
  if (typeof window === "undefined") return LOADING;
  if (raw === undefined) {
    try {
      raw = window.sessionStorage.getItem(KEY);
    } catch {
      raw = null;
    }
    snapshot = parse(raw);
  }
  return snapshot;
}

function parse(r: string | null): Session {
  if (!r) return ANON;
  try {
    const d = JSON.parse(r) as { token: string; user: User; isNew: boolean };
    return { status: "authed", token: d.token, user: d.user, isNew: d.isNew };
  } catch {
    return ANON;
  }
}

function write(r: string | null) {
  raw = r;
  snapshot = parse(r);
  try {
    if (r) window.sessionStorage.setItem(KEY, r);
    else window.sessionStorage.removeItem(KEY);
  } catch {
    // memory only
  }
  listeners.forEach((l) => l());
}

export function setSession(res: AuthResponse) {
  write(JSON.stringify({ token: res.access_token, user: res.user, isNew: res.is_new }));
}

export function markNotNew() {
  const s = read();
  if (s.status === "authed" && s.isNew) {
    write(JSON.stringify({ token: s.token, user: s.user, isNew: false }));
  }
}

export function logout() {
  write(null);
}

export function getToken(): string | null {
  const s = read();
  return s.status === "authed" ? s.token : null;
}

export function useSession(): Session {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    read,
    () => LOADING
  );
}

/** Where each role lands after login. */
export function homeFor(role: Role, isNew: boolean): string {
  if (role === "broker") return "/broker";
  return isNew ? "/chat" : "/home";
}
