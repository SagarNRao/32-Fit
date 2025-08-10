"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axios from "axios";
import { useAppContext } from "../appContext";
import { useRouter } from "next/navigation";

interface User {
  age: number;
  gender: "M" | "F";
  frequency: number;
  protein: number;
  calories: number;
  sleep: number;
  experience: "Beginner" | "Intermediate" | "Advanced";
  current_size_cm: number;
  workout_time_years: number;
}

interface Exercise {
  exercise_name: string;
  target_muscle_group: string;
  sets: number;
  reps: number;
  weight: number;
  exercise_category: "Compound" | "Isolation";
}

interface Prediction {
  [muscle: string]: number;
}

export default function WorkoutForm() {
  const { age, gender, chest, Back, Traps, Biceps } = useAppContext();
  const router = useRouter();

  const [targetMuscleGroup, setTargetMuscleGroup] = useState<number>(0);
  const [sets, setSets] = useState<number>(0);
  const [reps, setReps] = useState<number>(0);
  const [weight, setWeight] = useState<number>(0);
  const [exerciseCategory, setExerciseCategory] = useState<
    "Compound" | "Isolation"
  >("Compound");
  const [months, setMonths] = useState<number>(3);

  const [user] = useState<User>({
    age: age,
    gender: gender,
    frequency: 3,
    protein: 150,
    calories: 2800,
    sleep: 7.5,
    experience: "Intermediate",
    current_size_cm: chest, // Using chest measurement from context
    workout_time_years: 1,
  });

  const [workout, setWorkout] = useState<Exercise[]>([]);
  const [exercise, setExercise] = useState<Exercise>({
    exercise_name: "",
    target_muscle_group: "",
    sets: sets,
    reps: reps,
    weight: weight,
    exercise_category: exerciseCategory,
  });
  const [predictions, setPredictions] = useState<Prediction>({});
  const [error, setError] = useState<string | null>(null);

  const addExercise = () => {
    if (
      exercise.exercise_name &&
      exercise.target_muscle_group &&
      exercise.sets > 0 &&
      exercise.reps > 0 &&
      exercise.weight > 0 &&
      exercise.exercise_category
    ) {
      setWorkout([...workout, exercise]);
      setExercise({
        exercise_name: "",
        target_muscle_group: "",
        sets: 0,
        reps: 0,
        weight: 0,
        exercise_category: "Compound",
      });
    } else {
      setError("Please fill in all exercise fields");
    }
  };

  const callServer = async () => {
    try {
      setError(null);

      const updatedUser = {
        ...user,
        age: age,
        gender: gender,
        current_size_cm: chest, // Using chest as primary measurement
      };

      const response = await axios.post("http://localhost:3001/predict", {
        ...updatedUser,
        exercises: workout,
        time_months: months,
      });

      // Parse the response string into an object
      const predictionLines = response.data.result.split("\n");
      const predictionObj: Prediction = {};
      predictionLines.forEach((line: string) => {
        if (line && !line.includes("Error")) {
          const [muscle, value] = line.split(" growth: ");
          predictionObj[muscle] = parseFloat(value);
        }
      });
      setPredictions(predictionObj);
    } catch (error) {
      console.error("Error calling server:", error);
      setError("Failed to get predictions. Please try again.");
    }
  };

  return (
    <div>
      <div className="flex gap-4 p-4">
        <Card className="w-1/3 text-[#E1E2C1]">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Add Exercise</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select
              onValueChange={(value) =>
                setExercise({ ...exercise, exercise_name: value })
              }
              value={exercise.exercise_name}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select Exercise" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Chest Exercises</SelectLabel>
                  <SelectItem value="Barbell Bench Press">
                    Barbell Bench Press
                  </SelectItem>
                  <SelectItem value="Incline Barbell Bench Press">
                    Incline Barbell Bench Press
                  </SelectItem>
                  <SelectItem value="Dumbbell Bench Press">
                    Dumbbell Bench Press
                  </SelectItem>
                  <SelectItem value="Dumbbell Flyes">Dumbbell Flyes</SelectItem>
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Back Exercises</SelectLabel>
                  <SelectItem value="Barbell Rows">Barbell Rows</SelectItem>
                  <SelectItem value="Lat Pulldowns">Lat Pulldowns</SelectItem>
                  <SelectItem value="Pull-ups">Pull-ups</SelectItem>
                  <SelectItem value="Deadlifts">Deadlifts</SelectItem>
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Biceps Exercises</SelectLabel>
                  <SelectItem value="Barbell Curls">Barbell Curls</SelectItem>
                  <SelectItem value="Dumbbell Curls">Dumbbell Curls</SelectItem>
                  <SelectItem value="Hammer Curls">Hammer Curls</SelectItem>
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Legs Exercises</SelectLabel>
                  <SelectItem value="Squats">Squats</SelectItem>
                  <SelectItem value="Leg Press">Leg Press</SelectItem>
                  <SelectItem value="Leg Curls">Leg Curls</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
            <Select
              onValueChange={(value) =>
                setExercise({ ...exercise, target_muscle_group: value })
              }
              value={exercise.target_muscle_group}
            >
              <SelectTrigger>
                <SelectValue placeholder="Target Muscle Group" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Chest">Chest</SelectItem>
                <SelectItem value="Back">Back</SelectItem>
                <SelectItem value="Biceps">Biceps</SelectItem>
                <SelectItem value="Traps">Traps</SelectItem>
              </SelectContent>
            </Select>
            <Select
              onValueChange={(value) =>
                setExercise({
                  ...exercise,
                  exercise_category: value as "Compound" | "Isolation",
                })
              }
              value={exercise.exercise_category}
            >
              <SelectTrigger>
                <SelectValue placeholder="Exercise Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Compound">Compound</SelectItem>
                <SelectItem value="Isolation">Isolation</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="number"
              placeholder="Sets (1-10)"
              value={exercise.sets || ""}
              onChange={(e) =>
                setExercise({ ...exercise, sets: Number(e.target.value) })
              }
            />
            <Input
              type="number"
              placeholder="Reps (1-20)"
              value={exercise.reps || ""}
              onChange={(e) =>
                setExercise({ ...exercise, reps: Number(e.target.value) })
              }
            />
            <Input
              type="number"
              placeholder="Weight (kg)"
              value={exercise.weight || ""}
              onChange={(e) =>
                setExercise({ ...exercise, weight: Number(e.target.value) })
              }
            />
            <Input
              type="number"
              placeholder="Time (months)"
              value={months || ""}
              onChange={(e) => setMonths(Number(e.target.value))}
            />
            <Button
              className="bg-[#E66B31] text-[#E1E2C1]"
              onClick={addExercise}
            >
              Add Exercise
            </Button>
          </CardContent>
        </Card>

        <Card className="w-1/3 text-[#E1E2C1]">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">
              Workout Plan & Predictions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {workout.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold">Current Workout Plan:</h3>
                <ul className="list-disc pl-5">
                  {workout.map((ex, index) => (
                    <li key={index}>
                      {ex.exercise_name} ({ex.target_muscle_group}): {ex.sets}{" "}
                      sets x {ex.reps} reps @ {ex.weight}kg (
                      {ex.exercise_category})
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <Button
              className="bg-[#E66B31] text-[#E1E2C1]"
              onClick={callServer}
              disabled={workout.length === 0}
            >
              Get Predictions
            </Button>
            {error && <p className="text-red-500 mt-2">{error}</p>}
            {Object.keys(predictions).length > 0 && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold">
                  Predicted Muscle Growth:
                </h3>
                <ul className="list-disc pl-5">
                  {Object.entries(predictions).map(([muscle, growth]) => (
                    <li key={muscle}>
                      {muscle}: {growth.toFixed(2)} cm²
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="text-[#E1E2C1]">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">
              Current Measurements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 pl-30 pr-30 ">
              {[
                { label: "Chest", value: chest },
                { label: "Back", value: Back },
                { label: "Traps", value: Traps },
                { label: "Biceps", value: Biceps },
              ].map(({ label, value }) => (
                <div key={label} className="flex flex-col items-center">
                  <div className="w-24 h-24 rounded-full bg-[#E66B31] text-[#E1E2C1] flex items-center justify-center">
                    <span className="text-xl font-bold">{value}cm</span>
                  </div>
                  <span className="mt-2">{label}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
