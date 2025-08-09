import Image from "next/image";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <>
      <div>
        <Button onClick={() => window.location.href = '/profile'}>Get started</Button>
      </div>
    </>
  );
}
