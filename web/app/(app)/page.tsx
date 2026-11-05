import { Suspense } from "react";
import GamesView from "./GamesView";

export default function HomePage() {
  return (
    <Suspense fallback={null}>
      <GamesView />
    </Suspense>
  );
}
