export function SocialCard() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#141414",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 108,
            height: 108,
            borderRadius: 24,
            backgroundColor: "#cc9900",
            color: "#141414",
            fontSize: 64,
            fontWeight: 800,
          }}
        >
          R
        </div>
        <div style={{ display: "flex", fontSize: 72, fontWeight: 800, letterSpacing: -2, color: "#ededed" }}>
          RA Downloader
        </div>
      </div>
      <div
        style={{
          display: "flex",
          marginTop: 36,
          fontSize: 30,
          color: "#b4b4b4",
          maxWidth: 860,
          textAlign: "center",
        }}
      >
        Buscá y descargá ROMs compatibles con RetroAchievements
      </div>
      <div style={{ display: "flex", marginTop: 44, fontSize: 24, color: "#cc9900", fontWeight: 700 }}>
        8.460+ juegos indexados
      </div>
    </div>
  );
}
