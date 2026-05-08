"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  FolderOpen, 
  Activity, 
  TerminalSquare, 
  Settings,
  Database,
  LogOut
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

const routes = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { label: "Projects", icon: FolderOpen, href: "/projects" },
  { label: "Pipelines", icon: Activity, href: "/pipelines" },
  { label: "Logs", icon: TerminalSquare, href: "/logs" },
  { label: "Settings", icon: Settings, href: "/settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="flex flex-col h-full w-64 bg-card border-r border-border">
      <div className="p-6 flex items-center gap-3 border-b border-border">
        <div className="bg-primary/20 p-2 rounded-lg">
          <Database className="w-6 h-6 text-primary" />
        </div>
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-400">
          SchemaForge
        </span>
      </div>

      <div className="flex-1 py-6 px-4 flex flex-col gap-2">
        {routes.map((route) => (
          <Link
            key={route.href}
            href={route.href}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
              pathname.startsWith(route.href)
                ? "bg-primary/10 text-primary shadow-sm"
                : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
            )}
          >
            <route.icon className="w-5 h-5" />
            {route.label}
          </Link>
        ))}
      </div>

      <div className="p-4 border-t border-border">
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
