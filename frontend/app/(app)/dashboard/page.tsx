import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, DatabaseZap, ShieldAlert, Cpu } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Overview of your migration pipelines and system health.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-card/50 backdrop-blur-sm border-primary/20 shadow-[0_0_15px_rgba(59,130,246,0.05)] transition-all hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Pipelines</CardTitle>
            <Activity className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">2</div>
            <p className="text-xs text-green-400 mt-1">+1 started today</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur-sm border-blue-500/20 transition-all hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Chunks Converted</CardTitle>
            <DatabaseZap className="w-4 h-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">1,492</div>
            <p className="text-xs text-muted-foreground mt-1">Across all projects</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur-sm border-destructive/20 transition-all hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Validation Failures</CardTitle>
            <ShieldAlert className="w-4 h-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">14</div>
            <p className="text-xs text-destructive mt-1">Requiring manual review</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur-sm border-amber-500/20 transition-all hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Workers</CardTitle>
            <Cpu className="w-4 h-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">3 / 4</div>
            <p className="text-xs text-green-400 mt-1">System healthy</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Recent Pipelines</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-background/50 border border-border">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Activity className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-white">Core Banking Schema v{i}</p>
                      <p className="text-xs text-muted-foreground">Started 2 hours ago</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-green-400">75% Complete</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Worker Queue Depth</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">Parsing Queue</span>
                  <span className="text-sm text-muted-foreground">0 pending</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-green-400 h-2 rounded-full" style={{ width: '5%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">Conversion Queue</span>
                  <span className="text-sm text-muted-foreground">142 pending</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">AI Translation Queue</span>
                  <span className="text-sm text-muted-foreground">12 pending</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-amber-400 h-2 rounded-full" style={{ width: '15%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">Validation Queue</span>
                  <span className="text-sm text-muted-foreground">89 pending</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-purple-400 h-2 rounded-full" style={{ width: '35%' }}></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
