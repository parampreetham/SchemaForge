"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactDiffViewer from "react-diff-viewer-continued";
import { ArrowLeft, FileCode2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { pipelineService } from "@/services/pipeline-service";

export default function ArtifactViewerPage() {
  const params = useParams();
  const router = useRouter();
  const chunkId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [artifact, setArtifact] = useState<any>(null);

  useEffect(() => {
    const loadArtifact = async () => {
      try {
        const data = await pipelineService.getArtifact(chunkId);
        setArtifact(data);
      } catch (err) {
        console.error("Failed to load artifact", err);
      } finally {
        setLoading(false);
      }
    };
    if (chunkId) loadArtifact();
  }, [chunkId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (!artifact) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
        <FileCode2 className="w-12 h-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Artifact Not Found</h2>
        <Button variant="outline" onClick={() => router.back()}>Go Back</Button>
      </div>
    );
  }

  const oldCode = artifact.original_sql || "";
  const newCode = artifact.converted_sql || "";

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <FileCode2 className="w-6 h-6 text-primary" />
              Artifact: {artifact.chunk_id}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">Side-by-side comparison of DB2 source and T-SQL output</p>
          </div>
        </div>
      </div>

      <Card className="bg-card/50 backdrop-blur-sm border border-border/50">
        <CardHeader className="border-b border-border/50 pb-4">
          <CardTitle className="text-sm font-medium flex justify-between">
            <span className="text-muted-foreground">Original DB2 SQL</span>
            <span className="text-primary">Generated T-SQL</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0 overflow-hidden rounded-b-lg">
          <div className="h-[70vh] overflow-auto custom-scrollbar">
            <ReactDiffViewer
              oldValue={oldCode}
              newValue={newCode}
              splitView={true}
              useDarkTheme={true}
              leftTitle="DB2"
              rightTitle="T-SQL"
              styles={{
                variables: {
                  dark: {
                    diffViewerBackground: '#0f172a',
                    diffViewerColor: '#f8fafc',
                    addedBackground: '#16331a',
                    addedColor: '#ffffff',
                    removedBackground: '#3d1616',
                    removedColor: '#ffffff',
                    wordAddedBackground: '#285e30',
                    wordRemovedBackground: '#6b2626',
                    addedGutterBackground: '#132c16',
                    removedGutterBackground: '#2d1010',
                    gutterBackground: '#0b1120',
                    gutterColor: '#64748b',
                  }
                }
              }}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
