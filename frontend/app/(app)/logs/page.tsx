"use client";

import { useState, useEffect, useRef } from "react";
import { Terminal, Filter, RefreshCw, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/services/api-client";

interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  module: string;
  message: string;
}

export default function LogViewerPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      // Mocking API call for logs
      // const res = await apiClient.get('/system/logs?limit=100');
      // setLogs(res.data);
      
      // MVP Mock Data
      setTimeout(() => {
        setLogs([
          { id: 1, timestamp: new Date().toISOString(), level: "INFO", module: "app.main", message: "Starting SchemaForge API Server on port 8000" },
          { id: 2, timestamp: new Date().toISOString(), level: "INFO", module: "app.workers.parsing", message: "Parsing engine initialized." },
          { id: 3, timestamp: new Date().toISOString(), level: "WARNING", module: "app.services.ai", message: "OpenAI rate limit approaching (85%)." },
          { id: 4, timestamp: new Date().toISOString(), level: "ERROR", module: "app.services.validation", message: "Connection timeout to Azure SQL Target." },
          { id: 5, timestamp: new Date().toISOString(), level: "INFO", module: "app.workers.conversion", message: "Converted chunk_id=7482." },
        ]);
        setLoading(false);
      }, 500);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case "INFO": return "text-blue-400";
      case "WARNING": return "text-amber-400";
      case "ERROR": return "text-destructive font-bold";
      case "DEBUG": return "text-gray-500";
      default: return "text-white";
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Terminal className="w-8 h-8 text-primary" />
            System Logs
          </h1>
          <p className="text-muted-foreground mt-1">Real-time structured event logs from all backend workers.</p>
        </div>
        
        <div className="flex gap-3 bg-card/50 p-2 rounded-xl border border-border backdrop-blur-sm">
          <Button variant="outline" size="sm" className="gap-2">
            <Filter className="w-4 h-4" /> Filter
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="w-4 h-4" /> Export
          </Button>
          <Button variant="default" size="sm" className="gap-2" onClick={fetchLogs} disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </Button>
        </div>
      </div>

      <Card className="flex-1 bg-[#0a0f1a] border border-border shadow-[0_0_20px_rgba(0,0,0,0.5)] flex flex-col min-h-[60vh]">
        <CardHeader className="border-b border-border/50 py-3 bg-[#0f172a]/50">
          <CardTitle className="text-xs font-mono text-muted-foreground flex gap-4">
            <span className="w-48">TIMESTAMP</span>
            <span className="w-20">LEVEL</span>
            <span className="w-48">MODULE</span>
            <span className="flex-1">MESSAGE</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-y-auto font-mono text-xs custom-scrollbar">
          <div className="p-4 space-y-1">
            {logs.map((log) => (
              <div key={log.id} className="flex gap-4 hover:bg-white/5 p-1 rounded transition-colors group cursor-text">
                <span className="w-48 text-gray-500 select-none">
                  {new Date(log.timestamp).toISOString().replace('T', ' ').slice(0, -1)}
                </span>
                <span className={`w-20 select-none ${getLevelColor(log.level)}`}>
                  [{log.level}]
                </span>
                <span className="w-48 text-purple-400 select-none">
                  {log.module}
                </span>
                <span className={`flex-1 text-gray-300 group-hover:text-white transition-colors`}>
                  {log.message}
                </span>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
