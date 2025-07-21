import React from "react";
import { MultimodalPreview } from "./MultimodalPreview";
import { cn } from "@/lib/utils";
import type { UploadedFile } from "@/hooks/use-file-upload";

interface ContentBlocksPreviewProps {
  files: UploadedFile[];
  onRemove: (idx: number) => void;
  size?: "sm" | "md" | "lg";
  className?: string;
}

/**
 * Renders a preview of uploaded files with optional remove functionality.
 * Uses cn utility for robust class merging.
 */
export const ContentBlocksPreview: React.FC<ContentBlocksPreviewProps> = ({
  files,
  onRemove,
  size = "md",
  className,
}) => {
  if (!files.length) return null;
  return (
    <div className={cn("flex flex-wrap gap-2 p-3.5 pb-0", className)}>
      {files.map((file, idx) => (
        <MultimodalPreview
          key={idx}
          file={file}
          removable
          onRemove={() => onRemove(idx)}
          size={size}
        />
      ))}
    </div>
  );
};
