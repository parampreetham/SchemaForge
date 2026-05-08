"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Database, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const setToken = useAuthStore((state) => state.setToken);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Mock authentication for MVP frontend
    setTimeout(() => {
      setToken("mock_jwt_token_for_mvp");
      router.push("/dashboard");
    }, 1000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[40%] h-[50%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[50%] rounded-full bg-blue-600/20 blur-[120px] pointer-events-none" />

      <div className="w-full max-w-md p-8 rounded-2xl bg-card/40 backdrop-blur-xl border border-border shadow-2xl relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mb-4 border border-primary/30 shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            <Database className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Welcome Back
          </h1>
          <p className="text-muted-foreground mt-2">Sign in to SchemaForge</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-background/50 border border-border rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              placeholder="admin"
              required
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-300">Password</label>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background/50 border border-border rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          <Button 
            type="submit" 
            className="w-full h-12 mt-6 text-md font-semibold bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 shadow-[0_0_20px_rgba(59,130,246,0.3)] transition-all"
            disabled={loading}
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Sign In"}
          </Button>
        </form>
      </div>
    </div>
  );
}
