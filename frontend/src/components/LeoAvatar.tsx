import './LeoAvatar.css'

interface LeoAvatarProps {
  isSpeaking?: boolean
  isWorried?: boolean
}

const LeoAvatar = ({ isSpeaking = false, isWorried = false }: LeoAvatarProps) => {
  return (
    <div className="leo-container">
      {/* 🦁 This class toggles the 'speaking' animation in CSS */}
      <div className={`leo-avatar ${isSpeaking ? 'speaking' : ''} ${isWorried ? 'worried' : ''}`}>
        
        <svg viewBox="0 -30 240 330" className="leo-svg">
          <defs>
            <linearGradient id="fur" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#E8A838" />
              <stop offset="100%" stopColor="#D4942A" />
            </linearGradient>
            <radialGradient id="maneInner" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#8B5A2B" />
              <stop offset="100%" stopColor="#5D3A1A" />
            </radialGradient>
            <radialGradient id="snout" cx="50%" cy="30%" r="70%">
              <stop offset="0%" stopColor="#F5DEB3" />
              <stop offset="100%" stopColor="#DEC89A" />
            </radialGradient>
          </defs>

          {/* MANE */}
          <g className="mane">
            <circle cx="50" cy="60" r="35" fill="#3D2510"/>
            <circle cx="30" cy="90" r="32" fill="#3D2510"/>
            <circle cx="25" cy="125" r="30" fill="#3D2510"/>
            <circle cx="35" cy="160" r="30" fill="#3D2510"/>
            <circle cx="50" cy="185" r="30" fill="#3D2510"/>
            <circle cx="68" cy="205" r="28" fill="#3D2510"/>
            <circle cx="90" cy="222" r="26" fill="#3D2510"/>
            <circle cx="115" cy="235" r="24" fill="#3D2510"/>
            <circle cx="190" cy="60" r="35" fill="#3D2510"/>
            <circle cx="210" cy="90" r="32" fill="#3D2510"/>
            <circle cx="215" cy="125" r="30" fill="#3D2510"/>
            <circle cx="205" cy="160" r="30" fill="#3D2510"/>
            <circle cx="190" cy="185" r="30" fill="#3D2510"/>
            <circle cx="172" cy="205" r="28" fill="#3D2510"/>
            <circle cx="150" cy="222" r="26" fill="#3D2510"/>
            <circle cx="125" cy="235" r="24" fill="#3D2510"/>
            <circle cx="70" cy="25" r="32" fill="#3D2510"/>
            <circle cx="120" cy="10" r="35" fill="#3D2510"/>
            <circle cx="170" cy="25" r="32" fill="#3D2510"/>
            <circle cx="55" cy="55" r="32" fill="#4A2F15"/>
            <circle cx="38" cy="85" r="30" fill="#4A2F15"/>
            <circle cx="32" cy="118" r="28" fill="#4A2F15"/>
            <circle cx="42" cy="152" r="28" fill="#4A2F15"/>
            <circle cx="55" cy="175" r="28" fill="#4A2F15"/>
            <circle cx="72" cy="195" r="26" fill="#4A2F15"/>
            <circle cx="92" cy="212" r="24" fill="#4A2F15"/>
            <circle cx="110" cy="225" r="22" fill="#4A2F15"/>
            <circle cx="185" cy="55" r="32" fill="#4A2F15"/>
            <circle cx="202" cy="85" r="30" fill="#4A2F15"/>
            <circle cx="208" cy="118" r="28" fill="#4A2F15"/>
            <circle cx="198" cy="152" r="28" fill="#4A2F15"/>
            <circle cx="185" cy="175" r="28" fill="#4A2F15"/>
            <circle cx="168" cy="195" r="26" fill="#4A2F15"/>
            <circle cx="148" cy="212" r="24" fill="#4A2F15"/>
            <circle cx="130" cy="225" r="22" fill="#4A2F15"/>
            <circle cx="75" cy="28" r="30" fill="#4A2F15"/>
            <circle cx="120" cy="15" r="32" fill="#4A2F15"/>
            <circle cx="165" cy="28" r="30" fill="#4A2F15"/>
          </g>

          {/* TAIL */}
          <g className="tail">
            <path d="M 185 250 Q 210 220 215 170 Q 220 120 205 80" fill="none" stroke="#8B5A2B" strokeWidth="22" strokeLinecap="round"/>
            <path d="M 185 250 Q 210 220 215 170 Q 220 120 205 80" fill="none" stroke="#E8A838" strokeWidth="16" strokeLinecap="round"/>
            <ellipse cx="205" cy="75" rx="18" ry="24" fill="#5D3A1A"/>
          </g>

          {/* BODY */}
          <ellipse cx="120" cy="235" rx="72" ry="75" fill="url(#fur)"/>
          <ellipse cx="120" cy="248" rx="45" ry="48" fill="#FFF5E0" opacity="0.5"/>
          
          {/* PAWS */}
          <ellipse cx="75" cy="295" rx="28" ry="18" fill="url(#fur)"/>
          <ellipse cx="75" cy="300" rx="18" ry="12" fill="#FFE4B5"/>
          <ellipse cx="165" cy="295" rx="28" ry="18" fill="url(#fur)"/>
          <ellipse cx="165" cy="300" rx="18" ry="12" fill="#FFE4B5"/>

          {/* EARS */}
          <ellipse cx="62" cy="65" rx="28" ry="30" fill="url(#fur)" stroke="#C68D30" strokeWidth="1"/>
          <ellipse cx="62" cy="70" rx="15" ry="17" fill="#E8B0A0"/>
          <ellipse cx="178" cy="65" rx="28" ry="30" fill="url(#fur)" stroke="#C68D30" strokeWidth="1"/>
          <ellipse cx="178" cy="70" rx="15" ry="17" fill="#E8B0A0"/>

          {/* FACE */}
          <ellipse cx="120" cy="115" rx="90" ry="75" fill="url(#fur)"/>
          <ellipse cx="120" cy="155" rx="48" ry="40" fill="url(#snout)"/>

          {/* EYES */}
          <g className="eyes">
            <ellipse cx="85" cy="105" rx="22" ry="24" fill="white"/>
            <ellipse cx="85" cy="107" rx="14" ry="17" fill="#5D3319" className="pupil"/>
            <circle cx="79" cy="100" r="6" fill="white"/>
            <ellipse cx="155" cy="105" rx="22" ry="24" fill="white"/>
            <ellipse cx="155" cy="107" rx="14" ry="17" fill="#5D3319" className="pupil"/>
            <circle cx="161" cy="100" r="6" fill="white"/>
          </g>

          <ellipse cx="120" cy="145" rx="12" ry="9" fill="#222"/>
          <path d="M 120 154 L 120 166" fill="none" stroke="#333" strokeWidth="2.5" strokeLinecap="round"/>

          {/* MOUTH - ANIMATED */}
          <g className="mouth">
            <g className="mouth-closed">
              <path d="M 95 170 Q 107 182 120 170 Q 133 182 145 170" fill="none" stroke="#333" strokeWidth="2.5" strokeLinecap="round"/>
            </g>
            <g className="mouth-open">
              <ellipse cx="120" cy="174" rx="22" ry="15" fill="#4A1515" stroke="#333" strokeWidth="2.5"/>
              <ellipse cx="120" cy="180" rx="12" ry="6" fill="#E57373"/>
            </g>
          </g>
          
          <circle cx="90" cy="158" r="2.5" fill="#8B6914"/>
          <circle cx="150" cy="158" r="2.5" fill="#8B6914"/>
        </svg>
      </div>
    </div>
  )
}

export default LeoAvatar