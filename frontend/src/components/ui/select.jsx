import React, { useState, useRef, useEffect } from 'react';

const Select = React.forwardRef(({ children, value, onValueChange, ...props }, ref) => {
  return React.cloneElement(children, { value, onValueChange, ...props });
});
Select.displayName = 'Select';

const SelectTrigger = React.forwardRef(({ className = '', children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={`flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});
SelectTrigger.displayName = 'SelectTrigger';

const SelectValue = React.forwardRef(({ placeholder, ...props }, ref) => {
  return (
    <span ref={ref} {...props}>
      {props.children || placeholder}
    </span>
  );
});
SelectValue.displayName = 'SelectValue';

const SelectContent = React.forwardRef(({ children, className = '', ...props }, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef(null);
  const contentRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contentRef.current && !contentRef.current.contains(event.target) && 
          triggerRef.current && !triggerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative">
      <div ref={triggerRef} onClick={() => setIsOpen(!isOpen)}>
        {React.Children.map(children, child => {
          if (React.isValidElement(child) && child.type === SelectTrigger) {
            return React.cloneElement(child, { onClick: () => setIsOpen(!isOpen) });
          }
          return child;
        })}
      </div>
      
      {isOpen && (
        <div
          ref={contentRef}
          className={`absolute top-full left-0 z-50 w-full mt-1 bg-background border border-input rounded-md shadow-lg ${className}`}
          {...props}
        >
          {React.Children.map(children, child => {
            if (React.isValidElement(child) && child.type !== SelectTrigger) {
              return React.cloneElement(child, { 
                onSelect: (value) => {
                  setIsOpen(false);
                  if (props.onValueChange) props.onValueChange(value);
                }
              });
            }
            return null;
          })}
        </div>
      )}
    </div>
  );
});
SelectContent.displayName = 'SelectContent';

const SelectItem = React.forwardRef(({ className = '', value, children, onSelect, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={`relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground ${className}`}
      onClick={() => onSelect && onSelect(value)}
      {...props}
    >
      {children}
    </div>
  );
});
SelectItem.displayName = 'SelectItem';

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem };
