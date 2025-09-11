'use client';

import { useCallback, useEffect } from 'react';

export const useHandleClickOutside = (
  ref: React.RefObject<HTMLDivElement | null>,
  isOpen: boolean,
  onClose: () => void,
) => {
  const handleWindowClick = useCallback(
    (event: MouseEvent) => {
      const target = event.target as Node;
      if (ref.current && !ref.current.contains(target) && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose, ref],
  );

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose],
  );

  useEffect(() => {
    if (isOpen) {
      window.addEventListener('mousedown', handleWindowClick);
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('mousedown', handleWindowClick);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown, handleWindowClick, isOpen]);
};
