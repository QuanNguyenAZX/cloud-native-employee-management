import { FaGithub, FaLinkedinIn } from "react-icons/fa"
import { FaXTwitter } from "react-icons/fa6"

const socialLinks = [
  {
    icon: FaGithub,
    href: "https://github.com/fastapi/fastapi",
    label: "GitHub",
  },
  { icon: FaXTwitter, href: "https://x.com/fastapi", label: "X" },
  {
    icon: FaLinkedinIn,
    href: "https://linkedin.com/company/fastapi",
    label: "LinkedIn",
  },
]

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-white/8 bg-white/[0.02] px-6 py-4 backdrop-blur-xl">
      <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
        <p className="text-sm text-muted-foreground">
          Full Stack FastAPI Template - {currentYear}
        </p>
        <div className="flex items-center gap-4">
          {socialLinks.map(({ icon: Icon, href, label }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={label}
              className="rounded-full border border-white/8 bg-white/[0.03] p-2 text-muted-foreground transition-all duration-200 hover:-translate-y-0.5 hover:border-white/15 hover:bg-white/[0.06] hover:text-foreground"
            >
              <Icon className="h-4 w-4" />
            </a>
          ))}
        </div>
      </div>
    </footer>
  )
}
