import React from 'react';
import { Modal } from './Modal';

interface SuspensionAlertProps {
  isOpen: boolean;
  onClose: () => void;
  message?: string;
}

export const SuspensionAlert: React.FC<SuspensionAlertProps> = ({
  isOpen,
  onClose,
  message = '您的账户已被停用，请联系管理员'
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="账户已停用"
      size="sm"
    >
      <div className="text-center">
        {/* 警告图标 */}
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
          <svg
            className="h-6 w-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        
        {/* 提示信息 */}
        <p className="text-sm text-gray-600 mb-6">
          {message}
        </p>
        
        {/* 操作按钮 */}
        <div className="flex justify-center">
          <button
            onClick={onClose}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
          >
            我知道了
          </button>
        </div>
      </div>
    </Modal>
  );
};
