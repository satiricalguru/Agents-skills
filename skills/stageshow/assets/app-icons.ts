// Original letter tiles used in place of the upstream app-bundle artwork.
function letterTile(label: string, background: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="${background}"/><text x="32" y="44" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="700" font-size="34" fill="white">${label}</text></svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

export const mail = letterTile('M', '#235db8')
export const calendar = letterTile('C', '#b43a46')
export const testFlight = letterTile('T', '#206d9c')
export const slack = letterTile('S', '#684675')
export const figma = letterTile('F', '#375e50')
export const notion = letterTile('N', '#24262b')
