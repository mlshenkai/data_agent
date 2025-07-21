import React from "react";
import { File, Image as ImageIcon, X as XIcon, Table, FileSpreadsheet } from "lucide-react";
import { cn } from "@/lib/utils";
import Image from "next/image";
import type { UploadedFile } from "@/hooks/use-file-upload";

export interface MultimodalPreviewProps {
  file: UploadedFile;
  removable?: boolean;
  onRemove?: () => void;
  className?: string;
  size?: "sm" | "md" | "lg";
}

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) {
    return `${bytes} B`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  } else {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
};

// Helper function to get file extension
const getFileExtension = (filename: string, mimeType: string): string => {
  if (filename.includes('.')) {
    const extension = filename.split('.').pop();
    return extension ? extension.toUpperCase() : '';
  }
  
  // Fallback based on mime type
  switch (mimeType) {
    case 'text/csv':
      return 'CSV';
    case 'application/vnd.ms-excel':
      return 'XLS';
    case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
      return 'XLSX';
    case 'application/pdf':
      return 'PDF';
    default:
      return '';
  }
};

export const MultimodalPreview: React.FC<MultimodalPreviewProps> = ({
  file,
  removable = false,
  onRemove,
  className,
  size = "md",
}) => {
  // Image file
  if (file.fileType.startsWith("image/")) {
    const imageUrl = `/${file.filePath}`;
    let imgClass: string = "rounded-md object-cover h-16 w-16 text-lg";
    if (size === "sm") imgClass = "rounded-md object-cover h-10 w-10 text-base";
    if (size === "lg") imgClass = "rounded-md object-cover h-24 w-24 text-xl";
    return (
      <div className={cn("relative inline-block", className)}>
        <Image
          src={imageUrl}
          alt={file.fileName}
          className={imgClass}
          width={size === "sm" ? 16 : size === "md" ? 32 : 48}
          height={size === "sm" ? 16 : size === "md" ? 32 : 48}
        />
        {removable && (
          <button
            type="button"
            className="absolute top-1 right-1 z-10 rounded-full bg-gray-500 text-white hover:bg-gray-700"
            onClick={onRemove}
            aria-label="Remove image"
          >
            <XIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }

  // CSV file
  if (file.fileType === "text/csv") {
    const fileSize = formatFileSize(file.fileSize);
    const fileExtension = getFileExtension(file.fileName, file.fileType);
    
    return (
      <div
        className={cn(
          "relative flex items-start gap-2 rounded-md border bg-blue-50 px-3 py-2",
          className,
        )}
      >
        <div className="flex flex-shrink-0 flex-col items-start justify-start">
          <Table
            className={cn(
              "text-blue-700",
              size === "sm" ? "h-5 w-5" : "h-7 w-7",
            )}
          />
        </div>
        <div className="min-w-0 flex-1">
          <span
            className={cn("text-sm break-all text-gray-800 font-medium")}
            style={{ wordBreak: "break-all", whiteSpace: "pre-wrap" }}
          >
            {file.fileName}
          </span>
          <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
            <span>CSV 数据文件</span>
            <span>•</span>
            <span>{fileSize}</span>
            {fileExtension && (
              <>
                <span>•</span>
                <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded text-xs font-medium">
                  {fileExtension}
                </span>
              </>
            )}
          </div>
        </div>
        {removable && (
          <button
            type="button"
            className="ml-2 self-start rounded-full bg-blue-200 p-1 text-blue-700 hover:bg-blue-300"
            onClick={onRemove}
            aria-label="Remove CSV file"
          >
            <XIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }

  // Excel file
  if (file.fileType === "application/vnd.ms-excel" ||
      file.fileType === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
    const fileSize = formatFileSize(file.fileSize);
    const fileExtension = getFileExtension(file.fileName, file.fileType);
    
    return (
      <div
        className={cn(
          "relative flex items-start gap-2 rounded-md border bg-green-50 px-3 py-2",
          className,
        )}
      >
        <div className="flex flex-shrink-0 flex-col items-start justify-start">
          <FileSpreadsheet
            className={cn(
              "text-green-700",
              size === "sm" ? "h-5 w-5" : "h-7 w-7",
            )}
          />
        </div>
        <div className="min-w-0 flex-1">
          <span
            className={cn("text-sm break-all text-gray-800 font-medium")}
            style={{ wordBreak: "break-all", whiteSpace: "pre-wrap" }}
          >
            {file.fileName}
          </span>
          <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
            <span>Excel 电子表格</span>
            <span>•</span>
            <span>{fileSize}</span>
            {fileExtension && (
              <>
                <span>•</span>
                <span className="bg-green-100 text-green-700 px-1.5 py-0.5 rounded text-xs font-medium">
                  {fileExtension}
                </span>
              </>
            )}
          </div>
        </div>
        {removable && (
          <button
            type="button"
            className="ml-2 self-start rounded-full bg-green-200 p-1 text-green-700 hover:bg-green-300"
            onClick={onRemove}
            aria-label="Remove Excel file"
          >
            <XIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }

  // PDF file
  if (file.fileType === "application/pdf") {
    const fileSize = formatFileSize(file.fileSize);
    const fileExtension = getFileExtension(file.fileName, file.fileType);
    
    return (
      <div
        className={cn(
          "relative flex items-start gap-2 rounded-md border bg-gray-100 px-3 py-2",
          className,
        )}
      >
        <div className="flex flex-shrink-0 flex-col items-start justify-start">
          <File
            className={cn(
              "text-teal-700",
              size === "sm" ? "h-5 w-5" : "h-7 w-7",
            )}
          />
        </div>
        <div className="min-w-0 flex-1">
          <span
            className={cn("text-sm break-all text-gray-800 font-medium")}
            style={{ wordBreak: "break-all", whiteSpace: "pre-wrap" }}
          >
            {file.fileName}
          </span>
          <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
            <span>PDF 文档</span>
            <span>•</span>
            <span>{fileSize}</span>
            {fileExtension && (
              <>
                <span>•</span>
                <span className="bg-teal-100 text-teal-700 px-1.5 py-0.5 rounded text-xs font-medium">
                  {fileExtension}
                </span>
              </>
            )}
          </div>
        </div>
        {removable && (
          <button
            type="button"
            className="ml-2 self-start rounded-full bg-gray-200 p-1 text-teal-700 hover:bg-gray-300"
            onClick={onRemove}
            aria-label="Remove PDF"
          >
            <XIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }

  // Fallback for unknown types
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-md border bg-gray-100 px-3 py-2 text-gray-500",
        className,
      )}
    >
      <File className="h-5 w-5 flex-shrink-0" />
      <span className="truncate text-xs">Unsupported file type</span>
      {removable && (
        <button
          type="button"
          className="ml-2 rounded-full bg-gray-200 p-1 text-gray-500 hover:bg-gray-300"
          onClick={onRemove}
          aria-label="Remove file"
        >
          <XIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};
