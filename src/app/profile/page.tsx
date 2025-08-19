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
import { Input } from "@/components/ui/input";

export default function Page() {
  const {
    userName,
    setUserName,
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
  const {
    Experience,
    setExperience,
    BFP,
    setBFP,
    currentWeight,
    setCurrentWeight,
    height,
    setHeight,
    geneticAdvantage,
    setGeneticAdvantage,
    workoutTimeYears,
    setWorkoutTimeYears,
  } = useAppContext();

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-md mx-auto">
        <Card>
          <CardContent className="p-6">
            <CardTitle>Profile Setup</CardTitle>
            <CardDescription>Please fill in your details</CardDescription>

            <form onSubmit={handleSave} className="mt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                />

                <label className="text-sm font-medium">Age</label>
                <Input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                />

                <label className="text-sm font-medium">Experience Level</label>
                <select
                  value={Experience}
                  onChange={(e) =>
                    setExperience(
                      e.target.value as "Beginner" | "Intermediate" | "Advanced"
                    )
                  }
                  className="w-full rounded-md border p-2"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>

                <label className="text-sm font-medium">
                  Body Fat Percentage
                </label>
                <Input
                  type="number"
                  value={BFP}
                  onChange={(e) => setBFP(Number(e.target.value))}
                />

                <label className="text-sm font-medium">
                  Current Weight (kg)
                </label>
                <Input
                  type="number"
                  value={currentWeight}
                  onChange={(e) => setCurrentWeight(Number(e.target.value))}
                />

                <label className="text-sm font-medium">Height (cm)</label>
                <Input
                  type="number"
                  value={height}
                  onChange={(e) => setHeight(Number(e.target.value))}
                />

                <label className="text-sm font-medium">Genetic Advantage (1-10)</label>
                <select
                  value={geneticAdvantage}
                  onChange={(e) =>
                    setGeneticAdvantage(Number(e.target.value) as 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10)
                  }
                  className="w-full rounded-md border p-2"
                >
                  {[1,2,3,4,5,6,7,8,9,10].map((num) => (
                    <option key={num} value={num}>{num}</option>
                  ))}
                </select>

                <label className="text-sm font-medium">
                  Years of Working Out
                </label>
                <Input
                  type="number"
                  value={workoutTimeYears}
                  onChange={(e) => setWorkoutTimeYears(Number(e.target.value))}
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
                  <Input
                    type="number"
                    value={chest}
                    onChange={(e) => setChest(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Back (cm)</label>
                  <Input
                    type="number"
                    value={Back}
                    onChange={(e) => setBack(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Traps (cm)</label>
                  <Input
                    type="number"
                    value={Traps}
                    onChange={(e) => setTraps(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Biceps (cm)</label>
                  <Input
                    type="number"
                    value={Biceps}
                    onChange={(e) => setBiceps(Number(e.target.value))}
                  />
                </div>
              </div>

              <Button type="submit" className="w-full">
                Save Profile & Go to Dashboard
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
  return (
    <div className="container mx-auto p-4">
      <div className="max-w-md mx-auto">
        <Card>
          <CardContent className="p-6">
            <CardTitle>Profile Setup</CardTitle>
            <CardDescription>Please fill in your details</CardDescription>

            <form onSubmit={handleSave} className="mt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                />
                <label className="text-sm font-medium">Age</label>
                <Input
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
                  <Input
                    type="number"
                    value={chest}
                    onChange={(e) => setChest(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Back (cm)</label>
                  <Input
                    type="number"
                    value={Back}
                    onChange={(e) => setBack(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Traps (cm)</label>
                  <Input
                    type="number"
                    value={Traps}
                    onChange={(e) => setTraps(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Biceps (cm)</label>
                  <Input
                    type="number"
                    value={Biceps}
                    onChange={(e) => setBiceps(Number(e.target.value))}
                    className="w-full rounded-md border p-2"
                  />
                </div>
              </div>

              <Button type="submit" className="w-full">
                Save Profile & Go to Dashboard
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
