import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-6xl font-bold mb-4">Get Started</h1>
        <Button>
          <Link href="/profile">Profile</Link>
        </Button>
      </div>
    </>
  );
}
