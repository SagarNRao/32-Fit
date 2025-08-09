"use client";

import React from "react";
import { useAppContext } from "../appContext";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function Page() {
  const {
    age,
    setAge,
    gender,
    setGender,
    chest,
    setChest,
    Back,
    setBack,
    Traps,
    setTraps,
    Biceps,
    setBiceps,
  } = useAppContext();

  const router = useRouter();

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault(); // Prevent form submission
    router.push("/dashboard");
  };

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-md mx-auto">
        <Card>
          <CardContent className="p-6">
            <CardTitle>Profile Setup</CardTitle>
            <CardDescription>Please fill in your details</CardDescription>

            <form onSubmit={handleSave} className="mt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  className="w-full rounded-md border p-2"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Gender</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as "M" | "F")}
                  className="w-full rounded-md border p-2"
                >
                  <option value="">Select gender</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Chest (cm)</label>
                  <input
                    type="number"
                    value={chest}
                    onChange={(e) => setChest(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Back (cm)</label>
                  <input
                    type="number"
                    value={Back}
                    onChange={(e) => setBack(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Traps (cm)</label>
                  <input
                    type="number"
                    value={Traps}
                    onChange={(e) => setTraps(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Biceps (cm)</label>
                  <input
                    type="number"
                    value={Biceps}
                    onChange={(e) => setBiceps(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
              </div>

              <Button type="submit" className="w-full">Save Profile & Go to Dashboard</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
