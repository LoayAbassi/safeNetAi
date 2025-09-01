import React from 'react';

const Alert = React.forwardRef(({ className = '', variant = 'default', children, ...props }, ref) => {
  const baseClasses = 'relative w-full rounded-lg border p-4';
  
  const variants = {
    default: 'bg-background text-foreground',
    destructive: 'border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive'
  };
  
  const classes = `${baseClasses} ${variants[variant]} ${className}`;
  
  return (
    <div ref={ref} className={classes} {...props}>
      {children}
    </div>
  );
});
Alert.displayName = 'Alert';

const AlertDescription = React.forwardRef(({ className = '', children, ...props }, ref) => {
  return (
    <div ref={ref} className={`text-sm [&_p]:leading-relaxed ${className}`} {...props}>
      {children}
    </div>
  );
});
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertDescription };
