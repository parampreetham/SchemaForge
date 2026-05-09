"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileDown, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { pipelineService } from "@/services/pipeline-service";

export default function NewPipelinePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    try {
      const result = await pipelineService.uploadSchema(file);
      // Once uploaded, start the pipeline processing automatically
      await pipelineService.startPipeline(result.id);
      // Redirect to the pipeline detail page
      router.push(`/projects/default/pipelines/${result.id}`);
    } catch (err) {
      console.error("Failed to upload file", err);
      alert("Upload failed. Check the console for details.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-2xl mx-auto mt-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
          <Upload className="w-8 h-8 text-primary" />
          Create Migration Pipeline
        </h1>
        <p className="text-muted-foreground mt-1">Upload your DB2 schema file to begin the AI-assisted conversion to Azure SQL.</p>
      </div>

      <Card className="bg-card/50 backdrop-blur-sm border border-border/50">
        <CardHeader>
          <CardTitle>Source Database Schema</CardTitle>
          <CardDescription>Upload a .sql or .ddl file exported from your source DB2 instance.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="border-2 border-dashed border-border/50 rounded-xl p-12 text-center hover:bg-white/5 transition-colors cursor-pointer relative">
            <input 
              type="file" 
              accept=".sql,.ddl" 
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 bg-primary/10 rounded-full">
                <FileDown className="w-8 h-8 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">
                  {file ? file.name : "Click to browse or drag and drop"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Supports .sql and .ddl files up to 500MB"}
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-4">
            <Button variant="outline" onClick={() => router.back()} disabled={uploading}>
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={!file || uploading} className="min-w-[120px]">
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                "Start Migration"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
