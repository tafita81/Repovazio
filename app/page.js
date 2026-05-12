import { redirect } from "next/navigation";

export default function Home() {
  // Redirecionar para o Dashboard V11 (Central de Controle React)
  redirect("/dashboard");
}
