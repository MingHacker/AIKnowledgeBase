import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentPlusIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';
import apiService from '../../services/api';
import toast from 'react-hot-toast';

interface DocumentUploadProps {
  onUploadComplete: () => void;
}

interface UploadStatus {
  file: File;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  documentId?: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [uploadStatuses, setUploadStatuses] = useState<UploadStatus[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    // Initialize upload statuses
    const newStatuses: UploadStatus[] = acceptedFiles.map(file => ({
      file,
      status: 'uploading' as const,
    }));
    
    setUploadStatuses(prev => [...prev, ...newStatuses]);

    // Upload files
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      const statusIndex = uploadStatuses.length + i;

      try {
        // Upload file
        const document = await apiService.uploadDocument(file);
        
        setUploadStatuses(prev => prev.map((status, index) => 
          index === statusIndex 
            ? { ...status, status: 'processing', documentId: document.id }
            : status
        ));

        // Start processing
        await apiService.processDocument(document.id);
        
        setUploadStatuses(prev => prev.map((status, index) => 
          index === statusIndex 
            ? { ...status, status: 'completed' }
            : status
        ));

        toast.success(`${file.name} uploaded and processed successfully!`);
        
      } catch (error: any) {
        console.error('Upload failed:', error);
        setUploadStatuses(prev => prev.map((status, index) => 
          index === statusIndex 
            ? { ...status, status: 'error', error: error.message || 'Upload failed' }
            : status
        ));
        
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    // Refresh documents list
    onUploadComplete();
  }, [uploadStatuses.length, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const clearCompleted = () => {
    setUploadStatuses(prev => prev.filter(status => 
      status.status !== 'completed' && status.status !== 'error'
    ));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
        );
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusText = (status: UploadStatus) => {
    switch (status.status) {
      case 'uploading':
        return 'Uploading...';
      case 'processing':
        return 'Processing...';
      case 'completed':
        return 'Completed';
      case 'error':
        return status.error || 'Error';
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive ? (
            'Drop the PDF files here...'
          ) : (
            <>
              <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
            </>
          )}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          PDF files only, up to 50MB each
        </p>
      </div>

      {/* Upload Status */}
      {uploadStatuses.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Upload Progress</h3>
            {uploadStatuses.some(s => s.status === 'completed' || s.status === 'error') && (
              <button
                onClick={clearCompleted}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear completed
              </button>
            )}
          </div>
          
          <div className="divide-y divide-gray-200">
            {uploadStatuses.map((status, index) => (
              <div key={index} className="px-4 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <DocumentPlusIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {status.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(status.file.size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`text-xs ${
                    status.status === 'completed' ? 'text-green-600' :
                    status.status === 'error' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {getStatusText(status)}
                  </span>
                  {getStatusIcon(status.status)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;