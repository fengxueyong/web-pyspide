import { h } from 'vue'

/**
 * 集中管理 SVG 图标（风格参考 lucide）
 * 使用方式：<component :is="Icons.play" :size="14" />
 */

function icon(paths) {
  const attrRe = /(\w+)=["']([^"']*)["']/g
  const children = paths.map(p => {
    const spaceIdx = p.indexOf(' ')
    const tag = spaceIdx === -1 ? p : p.slice(0, spaceIdx)
    const attrsStr = spaceIdx === -1 ? '' : p.slice(spaceIdx + 1)
    const attrs = {}
    let m
    while ((m = attrRe.exec(attrsStr)) !== null) {
      attrs[m[1]] = m[2]
    }
    return { tag, attrs }
  })
  return {
    render() {
      const size = this.$props.size || 14
      return h('svg', {
        width: size,
        height: size,
        viewBox: '0 0 24 24',
        fill: 'none',
        stroke: 'currentColor',
        'stroke-width': 2,
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
      }, children.map(c => h(c.tag, { ...c.attrs })))
    },
    props: { size: { type: [Number, String], default: 14 } }
  }
}

export const Icons = {
  play: icon([
    'polygon points="5 3 19 12 5 21 5 3"',
  ]),
  square: icon([
    'rect x="6" y="6" width="12" height="12" rx="2"',
  ]),
  chevronDown: icon([
    'polyline points="6 9 12 15 18 9"',
  ]),
  chevronLeft: icon([
    'polyline points="15 18 9 12 15 6"',
  ]),
  chevronRight: icon([
    'polyline points="9 18 15 12 9 6"',
  ]),
  layers: icon([
    'polygon points="12 2 2 7 12 12 22 7 12 2"',
    'polyline points="2 17 12 22 22 17"',
    'polyline points="2 12 12 17 22 12"',
  ]),
  image: icon([
    'rect x="3" y="3" width="18" height="18" rx="2" ry="2"',
    'circle cx="8.5" cy="8.5" r="1.5"',
    'polyline points="21 15 16 10 5 21"',
  ]),
  video: icon([
    'polygon points="23 7 16 12 23 17 23 7"',
    'rect x="1" y="5" width="15" height="14" rx="2" ry="2"',
  ]),
  download: icon([
    'path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"',
    'polyline points="7 10 12 15 17 10"',
    'line x1="12" y1="15" x2="12" y2="3"',
  ]),
  checkCircle: icon([
    'path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"',
    'polyline points="22 4 12 14.01 9 11.01"',
  ]),
  alertCircle: icon([
    'circle cx="12" cy="12" r="10"',
    'line x1="12" y1="8" x2="12" y2="12"',
    'line x1="12" y1="16" x2="12.01" y2="16"',
  ]),
  filter: icon([
    'polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"',
  ]),
  search: icon([
    'circle cx="11" cy="11" r="8"',
    'line x1="21" y1="21" x2="16.65" y2="16.65"',
  ]),
  x: icon([
    'line x1="18" y1="6" x2="6" y2="18"',
    'line x1="6" y1="6" x2="18" y2="18"',
  ]),
  list: icon([
    'line x1="8" y1="6" x2="21" y2="6"',
    'line x1="8" y1="12" x2="21" y2="12"',
    'line x1="8" y1="18" x2="21" y2="18"',
    'line x1="3" y1="6" x2="3.01" y2="6"',
    'line x1="3" y1="12" x2="3.01" y2="12"',
    'line x1="3" y1="18" x2="3.01" y2="18"',
  ]),
  grid: icon([
    'rect x="3" y="3" width="7" height="7"',
    'rect x="14" y="3" width="7" height="7"',
    'rect x="3" y="14" width="7" height="7"',
    'rect x="14" y="14" width="7" height="7"',
  ]),
  database: icon([
    'ellipse cx="12" cy="5" rx="9" ry="3"',
    'path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"',
    'path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"',
  ]),
  activity: icon([
    'polyline points="22 12 18 12 15 21 9 3 6 12 2 12"',
  ]),
  zap: icon([
    'polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"',
  ]),
  externalLink: icon([
    'path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"',
    'polyline points="15 3 21 3 21 9"',
    'line x1="10" y1="14" x2="21" y2="3"',
  ]),
  shield: icon([
    'path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"',
  ]),
  wifi: icon([
    'path d="M5 13a4 4 0 0 1 0-8 4 4 0 0 1 0 8z"',
    'line x1="7" y1="8" x2="11" y2="8"',
    'path d="M12 3a9 9 0 0 1 9 9"',
    'path d="M12 7a5 5 0 0 1 5 5"',
  ]),
  wifiOff: icon([
    'line x1="1" y1="1" x2="23" y2="23"',
    'path d="M5 13a4 4 0 0 1 0-8 4 4 0 0 1 0 8z"',
    'line x1="7" y1="8" x2="11" y2="8"',
    'path d="M12 3a9 9 0 0 1 9 9"',
    'path d="M12 7a5 5 0 0 1 5 5"',
  ]),
  user: icon([
    'path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"',
    'circle cx="12" cy="7" r="4"',
  ]),
  lock: icon([
    'rect x="3" y="11" width="18" height="11" rx="2" ry="2"',
    'path d="M7 11V7a5 5 0 0 1 10 0v4"',
  ]),
  globe: icon([
    'circle cx="12" cy="12" r="10"',
    'line x1="2" y1="12" x2="22" y2="12"',
    'path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"',
  ]),
  panelLeftClose: icon([
    'rect x="3" y="3" width="18" height="18" rx="2"',
    'line x1="9" y1="3" x2="9" y2="21"',
    'polyline points="15 9 11 12 15 15"',
  ]),
  panelLeftOpen: icon([
    'rect x="3" y="3" width="18" height="18" rx="2"',
    'line x1="9" y1="3" x2="9" y2="21"',
    'polyline points="11 9 15 12 11 15"',
  ]),
}

export default Icons
