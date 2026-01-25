import './Tree.css'

interface TreeProps {
  className?: string
  flip?: boolean
}

const Tree = ({ className = '', flip = false }: TreeProps) => {
  const id = className.replace(/[^a-zA-Z]/g, '') || 'tree'
  
  return (
    <svg 
      className={`tree ${className}`}
      viewBox="0 0 200 300" 
      style={{ transform: flip ? 'scaleX(-1)' : undefined }}
    >
      <defs>
        {/* Trunk gradient - dark edges, lighter center */}
        <linearGradient id={`trunk-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#5D4037"/>
          <stop offset="20%" stopColor="#6D5040"/>
          <stop offset="40%" stopColor="#8B6B50"/>
          <stop offset="60%" stopColor="#8B6B50"/>
          <stop offset="80%" stopColor="#6D5040"/>
          <stop offset="100%" stopColor="#5D4037"/>
        </linearGradient>
        {/* Left branch gradient */}
        <linearGradient id={`branch-left-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#5D4037"/>
          <stop offset="30%" stopColor="#7D5A45"/>
          <stop offset="70%" stopColor="#7D5A45"/>
          <stop offset="100%" stopColor="#5D4037"/>
        </linearGradient>
        {/* Right branch gradient */}
        <linearGradient id={`branch-right-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#5D4037"/>
          <stop offset="30%" stopColor="#7D5A45"/>
          <stop offset="70%" stopColor="#7D5A45"/>
          <stop offset="100%" stopColor="#5D4037"/>
        </linearGradient>
      </defs>

      {/* === TRUNK - Main trunk === */}
      <path 
        d="M 80 300 
           L 80 180
           L 80 180
           L 120 180
           L 120 300
           Z"
        fill={`url(#trunk-${id})`}
      />
      
      {/* Left branch */}
      <path 
        d="M 80 180
           Q 75 160 55 130
           L 35 90
           L 55 85
           Q 70 115 85 155
           L 85 180
           Z"
        fill={`url(#branch-left-${id})`}
      />
      
      {/* Right branch */}
      <path 
        d="M 120 180
           Q 125 160 145 130
           L 165 90
           L 145 85
           Q 130 115 115 155
           L 115 180
           Z"
        fill={`url(#branch-right-${id})`}
      />

      {/* === FOLIAGE - Large cloud shapes === */}
      
      {/* Back layer - darkest green */}
      <ellipse cx="35" cy="110" rx="55" ry="50" fill="#3D7A3D"/>
      <ellipse cx="165" cy="105" rx="50" ry="48" fill="#3D7A3D"/>
      <ellipse cx="100" cy="85" rx="70" ry="60" fill="#3D7A3D"/>
      
      {/* Middle layer - medium green */}
      <ellipse cx="30" cy="95" rx="52" ry="48" fill="#4E9E4E"/>
      <ellipse cx="170" cy="90" rx="48" ry="45" fill="#4E9E4E"/>
      <ellipse cx="100" cy="70" rx="65" ry="55" fill="#4E9E4E"/>
      <ellipse cx="55" cy="80" rx="42" ry="38" fill="#4E9E4E"/>
      <ellipse cx="145" cy="75" rx="40" ry="36" fill="#4E9E4E"/>
      
      {/* Front layer - brighter green */}
      <ellipse cx="40" cy="82" rx="48" ry="42" fill="#5FB85F"/>
      <ellipse cx="160" cy="75" rx="45" ry="40" fill="#5FB85F"/>
      <ellipse cx="100" cy="55" rx="58" ry="50" fill="#5FB85F"/>
      <ellipse cx="65" cy="65" rx="38" ry="34" fill="#5FB85F"/>
      <ellipse cx="135" cy="60" rx="40" ry="35" fill="#5FB85F"/>
      
      {/* Highlight clouds - light green */}
      <ellipse cx="50" cy="68" rx="40" ry="35" fill="#7FCF7F"/>
      <ellipse cx="150" cy="62" rx="38" ry="33" fill="#7FCF7F"/>
      <ellipse cx="100" cy="42" rx="50" ry="42" fill="#7FCF7F"/>
      
      {/* Top highlights - lightest */}
      <ellipse cx="65" cy="50" rx="32" ry="28" fill="#9FDF9F"/>
      <ellipse cx="135" cy="45" rx="34" ry="29" fill="#9FDF9F"/>
      <ellipse cx="100" cy="25" rx="40" ry="32" fill="#9FDF9F"/>
    </svg>
  )
}

export default Tree
