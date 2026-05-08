"use client";

import { useState, useEffect } from "react";
import { Play, Pause, XCircle, RotateCcw, FileCode2, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PipelineDetailPage() {
  const [progress, setProgress] = useState(15);
  
  // Mock polling effect
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(p => (p < 100 ? p + 2 : 100));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-white">Migration Job #8842</h1>
            <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-semibold border border-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.3)]">
              RUNNING
            </span>
          </div>
          <p className="text-muted-foreground mt-1">Core Banking Schema v2.1</p>
        </div>
        
        <div className="flex gap-3 bg-card/50 p-2 rounded-xl border border-border backdrop-blur-sm">
          <Button variant="outline" size="sm" className="gap-2">
            <Pause className="w-4 h-4 text-amber-400" /> Pause
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <XCircle className="w-4 h-4 text-destructive" /> Cancel
          </Button>
          <Button variant="default" size="sm" className="gap-2 bg-gradient-to-r from-primary to-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.5)] border-0">
            <Play className="w-4 h-4" /> Start
          </Button>
        </div>
      </div>

      {/* Progress Section */}
      <Card className="bg-card/40 backdrop-blur-md border border-border/50 overflow-hidden relative">
        <div className="absolute top-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-primary to-purple-500 w-full opacity-50" />
        <CardHeader>
          <CardTitle className="text-lg flex justify-between">
            <span>Overall Progress</span>
            <span className="text-primary font-mono">{progress}%</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-secondary/50 rounded-full h-3 mb-6 overflow-hidden border border-border">
            <div 
              className="bg-gradient-to-r from-blue-500 to-primary h-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(59,130,246,0.8)] relative" 
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmZmZmIiBmaWxsLW9wYWNpdHk9IjAuMSIvPgo8L3N2Zz4=')] opacity-50" />
            </div>
          </div>
          
          <div className="grid grid-cols-4 gap-4 text-center">
            <div className="bg-background/50 rounded-lg p-3 border border-border/50 shadow-inner">
              <p className="text-sm font-medium text-muted-foreground mb-1">Parsing</p>
              <div className="flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span className="font-mono text-white">100%</span>
              </div>
            </div>
            <div className="bg-primary/5 rounded-lg p-3 border border-primary/20 shadow-[0_0_15px_rgba(59,130,246,0.05)]">
              <p className="text-sm font-medium text-primary mb-1">Conversion</p>
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4 text-primary animate-pulse" />
                <span className="font-mono text-white">{Math.min(100, progress + 45)}%</span>
              </div>
            </div>
            <div className="bg-background/50 rounded-lg p-3 border border-border/50">
              <p className="text-sm font-medium text-muted-foreground mb-1">AI Translation</p>
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4 text-amber-400" />
                <span className="font-mono text-white">12%</span>
              </div>
            </div>
            <div className="bg-background/50 rounded-lg p-3 border border-border/50">
              <p className="text-sm font-medium text-muted-foreground mb-1">Validation</p>
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4 text-purple-400" />
                <span className="font-mono text-white">5%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chunk Table Mock */}
      <Card className="bg-card/40 backdrop-blur-md border border-border/50">
        <CardHeader className="flex flex-row items-center justify-between border-b border-border/50 pb-4">
          <CardTitle className="text-lg">Database Chunks</CardTitle>
          <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Search objects..." 
              className="bg-background/50 border border-border rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-primary w-64 text-white"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground bg-secondary/30 uppercase border-b border-border/50">
                <tr>
                  <th className="px-6 py-4">Object Name</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Retries</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "CUSTOMERS_TB", type: "TABLE", status: "validated", color: "text-green-400", bg: "bg-green-400/10", border: "border-green-400/20" },
                  { name: "CALCULATE_INTEREST", type: "PROCEDURE", status: "needs_ai", color: "text-amber-400", bg: "bg-amber-400/10", border: "border-amber-400/20" },
                  { name: "TRANSACTION_LOG", type: "TABLE", status: "translating", color: "text-blue-400", bg: "bg-blue-400/10", border: "border-blue-400/20" },
                  { name: "CHECK_BALANCE_TRG", type: "TRIGGER", status: "failed_validation", color: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/20", retries: 3 },
                ].map((row, i) => (
                  <tr key={i} className="border-b border-border/30 hover:bg-secondary/20 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-200 flex items-center gap-2">
                      <FileCode2 className="w-4 h-4 text-muted-foreground" />
                      {row.name}
                    </td>
                    <td className="px-6 py-4 text-gray-400">{row.type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${row.color} ${row.bg} ${row.border}`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-400">{row.retries || 0} / 3</td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm" className="h-8 text-primary hover:text-primary hover:bg-primary/10">View Artifact</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
