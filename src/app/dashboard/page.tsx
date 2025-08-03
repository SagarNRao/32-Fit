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
  const [user, setUser] = useState<User>({
    age: 30,
    gender: "M",
    frequency: 3,
    protein: 150,
    calories: 2800,
    sleep: 7.5,
    experience: "Intermediate",
    current_size_cm: 0,
    workout_time_years: 1,
  });

  const [workout, setWorkout] = useState<Exercise[]>([]);
  const [exercise, setExercise] = useState<Exercise>({
    exercise_name: "",
    target_muscle_group: "",
    sets: 0,
    reps: 0,
    weight: 0,
    exercise_category: "Compound",
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
      const response = await axios.post("http://localhost:3001/predict", {
        ...user,
        exercises: workout,
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
    <div className="flex gap-4 p-4">
      <Card className="w-1/2">
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            type="number"
            placeholder="Age (18-100)"
            value={user.age || ''}
            onChange={(e) => setUser({ ...user, age: Number(e.target.value) })}
          />
          <Select
            onValueChange={(value) => setUser({ ...user, gender: value as "M" | "F" })}
            value={user.gender}
          >
            <SelectTrigger>
              <SelectValue placeholder="Gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="M">Male</SelectItem>
              <SelectItem value="F">Female</SelectItem>
            </SelectContent>
          </Select>
          <Input
            type="number"
            placeholder="Training Frequency (1-7 days/week)"
            value={user.frequency || ''}
            onChange={(e) => setUser({ ...user, frequency: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Protein Intake (g)"
            value={user.protein || ''}
            onChange={(e) => setUser({ ...user, protein: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Calories (kcal)"
            value={user.calories || ''}
            onChange={(e) => setUser({ ...user, calories: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Sleep (hours)"
            value={user.sleep || ''}
            onChange={(e) => setUser({ ...user, sleep: Number(e.target.value) })}
          />
          <Select
            onValueChange={(value) =>
              setUser({ ...user, experience: value as "Beginner" | "Intermediate" | "Advanced" })
            }
            value={user.experience}
          >
            <SelectTrigger>
              <SelectValue placeholder="Experience Level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Beginner">Beginner</SelectItem>
              <SelectItem value="Intermediate">Intermediate</SelectItem>
              <SelectItem value="Advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>
          <Input
            type="number"
            placeholder="Current Muscle Size (cm)"
            value={user.current_size_cm || ''}
            onChange={(e) => setUser({ ...user, current_size_cm: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Workout Time (years)"
            value={user.workout_time_years || ''}
            onChange={(e) => setUser({ ...user, workout_time_years: Number(e.target.value) })}
          />
        </CardContent>
      </Card>

      <Card className="w-1/2">
        <CardHeader>
          <CardTitle>Add Exercise</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Exercise Name"
            value={exercise.exercise_name}
            onChange={(e) => setExercise({ ...exercise, exercise_name: e.target.value })}
          />
          <Select
            onValueChange={(value) => setExercise({ ...exercise, target_muscle_group: value })}
            value={exercise.target_muscle_group}
          >
            <SelectTrigger>
              <SelectValue placeholder="Target Muscle Group" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Chest">Chest</SelectItem>
              <SelectItem value="Back">Back</SelectItem>
              <SelectItem value="Biceps">Biceps</SelectItem>
              <SelectItem value="Quads">Quads</SelectItem>
            </SelectContent>
          </Select>
          <Select
            onValueChange={(value) =>
              setExercise({ ...exercise, exercise_category: value as "Compound" | "Isolation" })
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
            value={exercise.sets || ''}
            onChange={(e) => setExercise({ ...exercise, sets: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Reps (1-20)"
            value={exercise.reps || ''}
            onChange={(e) => setExercise({ ...exercise, reps: Number(e.target.value) })}
          />
          <Input
            type="number"
            placeholder="Weight (kg)"
            value={exercise.weight || ''}
            onChange={(e) => setExercise({ ...exercise, weight: Number(e.target.value) })}
          />
          <Button onClick={addExercise}>Add Exercise</Button>
        </CardContent>
      </Card>

      <Card className="w-full">
        <CardHeader>
          <CardTitle>Workout Plan & Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          {workout.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Current Workout Plan:</h3>
              <ul className="list-disc pl-5">
                {workout.map((ex, index) => (
                  <li key={index}>
                    {ex.exercise_name} ({ex.target_muscle_group}): {ex.sets} sets x {ex.reps} reps @ {ex.weight}kg
                    ({ex.exercise_category})
                  </li>
                ))}
              </ul>
            </div>
          )}
          <Button onClick={callServer} disabled={workout.length === 0}>
            Get Predictions
          </Button>
          {error && <p className="text-red-500 mt-2">{error}</p>}
          {Object.keys(predictions).length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold">Predicted Muscle Growth:</h3>
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
    </div>
  );
}