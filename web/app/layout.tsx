import type { Metadata } from "next";
import { Geist_Mono, Montserrat, Poppins } from "next/font/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

const body = Poppins({ variable: "--font-body", subsets: ["latin"], weight: ["400", "500", "600"] });
const display = Montserrat({ variable: "--font-display", subsets: ["latin"], weight: ["600", "700"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Langfuse Ops Agent",
  description: "Agente de operaciones: Langfuse MCP + GitHub MCP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning className={`${body.variable} ${display.variable} ${geistMono.variable} dark h-full antialiased`}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `try{if(localStorage.getItem("theme")==="light")document.documentElement.classList.remove("dark")}catch(e){}`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <TooltipProvider>{children}</TooltipProvider>
      </body>
    </html>
  );
}
