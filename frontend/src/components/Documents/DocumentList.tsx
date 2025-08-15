import React, { useState, useEffect } from 'react';
import { Document } from '../../types';
import apiService from '../../services/api';
import toast from 'react-hot-toast';
import {
  DocumentTextIcon,
  TrashIcon,
  EyeIcon,
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

interface DocumentListProps {
  documents: Document[];
  onRefresh: () => void;
  loading: boolean;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onRefresh, loading }) => {
  const [processingStatuses, setProcessingStatuses] = useState<{ [key: string]: any }>({});

  const handleDelete = async (documentId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      await apiService.deleteDocument(documentId);
      toast.success('Document deleted successfully');
      onRefresh();
    } catch (error: any) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete document');
    }
  };

  const handleProcess = async (documentId: string) => {
    try {
      await apiService.processDocument(documentId);
      toast.success('Document processing started');
      onRefresh();
    } catch (error: any) {
      console.error('Processing failed:', error);
      toast.error('Failed to start processing');
    }
  };

  const checkProcessingStatus = async (documentId: string) => {
    try {
      const status = await apiService.getProcessingStatus(documentId);
      setProcessingStatuses(prev => ({ ...prev, [documentId]: status }));
    } catch (error) {
      console.error('Failed to get processing status:', error);
    }
  };

  useEffect(() => {
    // Check processing status for documents that are being processed
    const processingDocs = documents.filter(doc => 
      doc.processing_status === 'pending' || 
      doc.processing_status === 'extracting' || 
      doc.processing_status === 'chunking' || 
      doc.processing_status === 'embedding'
    );

    processingDocs.forEach(doc => {
      checkProcessingStatus(doc.id);
    });
  }, [documents]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
      case 'embedding_failed':
      case 'chunking_failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      case 'pending':
      case 'extracting':
      case 'chunking':
      case 'embedding':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Ready';
      case 'pending':
        return 'Pending';
      case 'extracting':
        return 'Extracting Text';
      case 'chunking':
        return 'Creating Chunks';
      case 'embedding':
        return 'Generating Embeddings';
      case 'failed':
        return 'Failed';
      case 'embedding_failed':
        return 'Embedding Failed';
      case 'chunking_failed':
        return 'Chunking Failed';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading documents...</span>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by uploading your first PDF document.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {documents.map((document) => {
          const status = processingStatuses[document.id];
          
          return (
            <li key={document.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400 mr-3" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {document.original_filename}
                      </p>
                      <div className="ml-2 flex items-center">
                        {getStatusIcon(document.processing_status)}
                        <span className={`ml-1 text-xs ${
                          document.processing_status === 'completed' ? 'text-green-600' :
                          document.processing_status.includes('failed') ? 'text-red-600' :
                          'text-yellow-600'
                        }`}>
                          {getStatusText(document.processing_status)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="mt-1 flex items-center text-sm text-gray-500 space-x-4">
                      <span>{formatFileSize(document.file_size_bytes)}</span>
                      {document.total_pages && (
                        <span>{document.total_pages} pages</span>
                      )}
                      <span>Uploaded {formatDate(document.created_at)}</span>
                    </div>

                    {status && (
                      <div className="mt-2">
                        <div className="text-xs text-gray-600">
                          Processing: {status.chunks.total} chunks created, 
                          {status.chunks.with_embeddings} embedded ({status.chunks.embedding_progress.toFixed(1)}%)
                        </div>
                        {status.chunks.embedding_progress < 100 && (
                          <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                            <div 
                              className="bg-primary-600 h-1 rounded-full transition-all duration-300"
                              style={{ width: `${status.chunks.embedding_progress}%` }}
                            ></div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {document.processing_status !== 'completed' && (
                    <button
                      onClick={() => handleProcess(document.id)}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <ArrowPathIcon className="h-4 w-4 mr-1" />
                      Process
                    </button>
                  )}
                  
                  <button
                    onClick={() => checkProcessingStatus(document.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <EyeIcon className="h-4 w-4 mr-1" />
                    Status
                  </button>
                  
                  <button
                    onClick={() => handleDelete(document.id, document.original_filename)}
                    className="inline-flex items-center px-3 py-1.5 border border-red-300 shadow-sm text-xs font-medium rounded text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <TrashIcon className="h-4 w-4 mr-1" />
                    Delete
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default DocumentList;