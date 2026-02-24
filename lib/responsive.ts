/**
 * Responsive design utilities
 * Use these to ensure consistent responsive behavior across the app
 */

export const responsiveClasses = {
  // Padding
  pageX: 'px-4 md:px-6 lg:px-8',  // Page horizontal padding
  pageY: 'py-4 md:py-6 lg:py-8',  // Page vertical padding
  page: 'px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8',
  
  // Text sizes
  headingLg: 'text-2xl md:text-3xl lg:text-4xl',
  headingMd: 'text-xl md:text-2xl lg:text-3xl',
  headingSm: 'text-lg md:text-xl lg:text-2xl',
  
  // Grid layouts
  gridAuto: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6',
  gridWide: 'grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6',
  
  // Spacing
  spacingXs: 'space-y-2 md:space-y-3',
  spacingSm: 'space-y-3 md:space-y-4',
  spacingMd: 'space-y-4 md:space-y-6',
  spacingLg: 'space-y-6 md:space-y-8',
  
  // Container
  container: 'max-w-6xl mx-auto',
  containerLg: 'max-w-7xl mx-auto',
  containerSm: 'max-w-4xl mx-auto',
}

/**
 * Mobile-first responsive breakpoints
 */
export const breakpoints = {
  xs: 0,      // Extra small (phones)
  sm: 640,    // Small (portrait tablets)
  md: 768,    // Medium (landscape tablets, small laptops)
  lg: 1024,   // Large (laptops)
  xl: 1280,   // Extra large (large laptops)
  '2xl': 1536 // 2XL (desktop monitors)
}

/**
 * Utility to check if device is mobile
 */
export const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < breakpoints.md
}

/**
 * Utility to check if device is tablet
 */
export const isTablet = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth >= breakpoints.md && window.innerWidth < breakpoints.lg
}

/**
 * Utility to check if device is desktop
 */
export const isDesktop = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth >= breakpoints.lg
}
