import type { Metadata } from "next";
import MH370Experience from "@/components/MH370Experience";

export const metadata: Metadata = {
  title: "MH370 | Theories and Evidence",
  description:
    "An APUSH project about Malaysia Airlines Flight 370, the controversies around it, and the evidence behind the major theories.",
};

export default function MH370Page() {
  return <MH370Experience />;
}
