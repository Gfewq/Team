import './Tree.css'

interface TreeProps {
  className?: string
  flip?: boolean
}

const Tree = ({ className = '', flip = false }: TreeProps) => {
  return (
    <svg 
      className={`tree ${className}`}
      viewBox="0 0 220 300" 
      style={{ transform: flip ? 'scaleX(-1)' : undefined }}
    >
      {/* Main trunk - solid shape */}
      <path 
        d="M 95 300 
           C 95 260 90 230 88 200
           C 86 170 82 150 75 130
           L 60 100
           L 75 105
           C 85 120 90 140 95 160
           C 100 140 105 120 115 105
           L 130 100
           L 115 130
           C 108 150 104 170 102 200
           C 100 230 95 260 95 300
           Z"
        fill="#8B5A2B"
        stroke="#5D4037"
        strokeWidth="2"
      />
      {/* Trunk highlight */}
      <path 
        d="M 95 300 
           C 95 260 93 230 92 200
           C 91 170 90 150 88 140
           L 95 160
           C 100 150 102 140 104 140
           C 102 150 101 170 100 200
           C 99 230 97 260 97 300
           Z"
        fill="#A67C52"
      />
      {/* Left branch */}
      <path 
        d="M 75 130 Q 55 110 40 85"
        fill="none"
        stroke="#8B5A2B"
        strokeWidth="14"
        strokeLinecap="round"
      />
      {/* Right branch */}
      <path 
        d="M 115 130 Q 135 110 155 90"
        fill="none"
        stroke="#8B5A2B"
        strokeWidth="12"
        strokeLinecap="round"
      />
      
      {/* === FOLIAGE - lots of overlapping leaves === */}
      
      {/* Back shadow layer - darkest */}
      <ellipse cx="40" cy="100" rx="38" ry="32" fill="#2E7D32" stroke="#1B5E20" strokeWidth="2"/>
      <ellipse cx="110" cy="85" rx="50" ry="40" fill="#2E7D32" stroke="#1B5E20" strokeWidth="2"/>
      <ellipse cx="170" cy="95" rx="36" ry="30" fill="#2E7D32" stroke="#1B5E20" strokeWidth="2"/>
      <ellipse cx="75" cy="75" rx="42" ry="35" fill="#2E7D32" stroke="#1B5E20" strokeWidth="2"/>
      <ellipse cx="145" cy="80" rx="40" ry="33" fill="#2E7D32" stroke="#1B5E20" strokeWidth="2"/>
      
      {/* Middle layer - main green */}
      <ellipse cx="30" cy="90" rx="35" ry="30" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="60" cy="70" rx="40" ry="34" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="110" cy="60" rx="48" ry="38" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="160" cy="75" rx="38" ry="32" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="185" cy="88" rx="30" ry="26" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="85" cy="55" rx="36" ry="30" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      <ellipse cx="135" cy="58" rx="38" ry="32" fill="#43A047" stroke="#2E7D32" strokeWidth="2"/>
      
      {/* Front layer - brighter green */}
      <ellipse cx="45" cy="75" rx="32" ry="27" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="80" cy="50" rx="34" ry="28" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="110" cy="42" rx="40" ry="32" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="145" cy="52" rx="36" ry="30" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="175" cy="70" rx="30" ry="25" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="65" cy="60" rx="28" ry="24" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      <ellipse cx="125" cy="48" rx="32" ry="26" fill="#4CAF50" stroke="#388E3C" strokeWidth="2"/>
      
      {/* Highlight layer - lightest green */}
      <ellipse cx="55" cy="62" rx="24" ry="20" fill="#66BB6A" stroke="#4CAF50" strokeWidth="2"/>
      <ellipse cx="95" cy="38" rx="28" ry="22" fill="#66BB6A" stroke="#4CAF50" strokeWidth="2"/>
      <ellipse cx="130" cy="42" rx="26" ry="21" fill="#66BB6A" stroke="#4CAF50" strokeWidth="2"/>
      <ellipse cx="160" cy="58" rx="22" ry="18" fill="#66BB6A" stroke="#4CAF50" strokeWidth="2"/>
      <ellipse cx="75" cy="48" rx="22" ry="18" fill="#66BB6A" stroke="#4CAF50" strokeWidth="2"/>
      
      {/* Top highlights - brightest spots */}
      <ellipse cx="85" cy="32" rx="20" ry="16" fill="#81C784" stroke="#66BB6A" strokeWidth="1"/>
      <ellipse cx="115" cy="28" rx="22" ry="17" fill="#81C784" stroke="#66BB6A" strokeWidth="1"/>
      <ellipse cx="145" cy="40" rx="18" ry="14" fill="#81C784" stroke="#66BB6A" strokeWidth="1"/>
      <ellipse cx="60" cy="52" rx="16" ry="13" fill="#81C784" stroke="#66BB6A" strokeWidth="1"/>
      
      {/* Tiny accent highlights */}
      <ellipse cx="100" cy="20" rx="14" ry="11" fill="#A5D6A7"/>
      <ellipse cx="70" cy="40" rx="12" ry="10" fill="#A5D6A7"/>
      <ellipse cx="135" cy="35" rx="13" ry="10" fill="#A5D6A7"/>
    </svg>
  )
}

export default Tree
