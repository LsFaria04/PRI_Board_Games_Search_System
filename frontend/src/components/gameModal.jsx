import { useState, useEffect } from 'react'

export default function GameModal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Close button at the top-right */}
        <button className="modal-close" onClick={onClose}>
          ✖
        </button>

        {/* Modal body */}
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
}
