import { ImageResponse } from "next/og";
import { SocialCard } from "./social-card";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(<SocialCard />, size);
}
