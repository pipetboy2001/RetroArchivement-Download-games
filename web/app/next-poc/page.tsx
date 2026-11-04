export default function NextPocPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md text-center space-y-3">
        <h1 className="text-2xl font-bold text-gray-800">Next.js + Python conviven en este deploy 🎮</h1>
        <p className="text-gray-600">
          Esta página es Next.js/TypeScript (servicio <code>web</code>). El resto del sitio
          (<code>/</code>, <code>/games</code>, <code>/dl</code>, etc.) sigue siendo el Flask
          existente (servicio <code>api</code>), sin cambios.
        </p>
        <p className="text-sm text-gray-400">Prueba de infraestructura — issue #19</p>
      </div>
    </main>
  );
}
