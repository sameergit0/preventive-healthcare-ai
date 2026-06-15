import { Link } from 'react-router-dom'
import {
  Activity, ArrowRight, BarChart3, Heart, Shield,
  Sparkles, Footprints, Moon, Droplet, Brain,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

const features = [
  {
    icon: BarChart3,
    title: 'Smart Analytics',
    description: 'Get deep insights into your health with AI-powered scoring that combines daily metrics, lifestyle, and medical context.',
    color: 'bg-primary text-primary-on',
  },
  {
    icon: Heart,
    title: 'Risk-Aware Coaching',
    description: 'Receive personalized recommendations that factor in your medical history — from diabetes management to cardiac health.',
    color: 'bg-error text-error-on',
  },
  {
    icon: Shield,
    title: 'Holistic Scoring',
    description: 'Your health score combines 7 daily metrics with lifestyle habits, physical profile, and medical conditions for a 360° view.',
    color: 'bg-tertiary text-tertiary-on',
  },
  {
    icon: Sparkles,
    title: 'Actionable Insights',
    description: 'Correlations between your habits are detected automatically — like how screen time affects your sleep quality.',
    color: 'bg-secondary-container text-secondary-on-container',
  },
]

const metrics = [
  { icon: Footprints, label: 'Steps', value: '10,000', color: 'text-primary' },
  { icon: Moon, label: 'Sleep', value: '8h', color: 'text-tertiary' },
  { icon: Droplet, label: 'Water', value: '2.5L', color: 'text-primary' },
  { icon: Brain, label: 'Stress', value: '1-5', color: 'text-error' },
]

export function HomePage() {
  return (
    <div className="min-h-svh bg-background">
      {/* Navbar */}
      <header className="sticky top-0 z-30 border-b border-outline-variant/30 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-on">
              <Activity className="h-5 w-5" />
            </div>
            <span className="text-headline-md font-heading font-bold text-on-surface">Vitality</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Button variant="ghost" size="sm">Log in</Button>
            </Link>
            <Link to="/signup">
              <Button size="sm">Get Started <ArrowRight className="h-4 w-4" /></Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Gradient background elements */}
        <div className="pointer-events-none absolute -top-32 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
        <div className="pointer-events-none absolute -top-20 right-0 h-[400px] w-[400px] rounded-full bg-tertiary/5 blur-3xl" />

        <div className="mx-auto max-w-6xl px-6 pb-20 pt-16 sm:pb-28 sm:pt-24">
          <div className="flex flex-col items-center text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary-fixed px-4 py-1.5 text-label-lg text-on-primary-fixed-variant">
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Preventive Healthcare</span>
            </div>
            <h1 className="max-w-3xl text-5xl font-heading font-extrabold leading-tight tracking-tight text-on-surface sm:text-6xl lg:text-7xl">
              Your health,{' '}
              <span className="bg-gradient-to-r from-primary to-tertiary bg-clip-text text-transparent">
                quantified
              </span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-on-surface-variant sm:text-xl">
              Track daily metrics, understand your risks, and get personalized coaching — 
              all in one place. Vitality combines your behavior, lifestyle, and medical history
              into a single health score.
            </p>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="px-8 text-lg shadow-level-2 hover:shadow-level-3 transition-shadow">
                  Get Started Free <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg" className="px-8 text-lg">
                  Log in
                </Button>
              </Link>
            </div>
          </div>

          {/* Floating metric pills */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-3">
            {metrics.map((m) => (
              <div
                key={m.label}
                className="flex items-center gap-2 rounded-full bg-surface-container-lowest px-5 py-2.5 shadow-level-1 transition-transform hover:scale-105"
              >
                <m.icon className={`h-5 w-5 ${m.color}`} />
                <span className="text-body-md font-semibold text-on-surface">{m.label}</span>
                <span className="text-body-sm text-on-surface-variant">{m.value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="bg-surface-container-low/50 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-center">
            <h2 className="text-3xl font-heading font-bold text-on-surface sm:text-4xl">
              Everything you need for preventive health
            </h2>
            <p className="mt-3 text-body-lg text-on-surface-variant">
              More than a tracker — a personal health intelligence engine.
            </p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2">
            {features.map((f) => (
              <Card key={f.title} className="flex flex-col gap-4 transition-shadow hover:shadow-level-2">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${f.color}`}>
                  <f.icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-headline-md font-bold text-on-surface">{f.title}</h3>
                  <p className="mt-1.5 text-body-md text-on-surface-variant leading-relaxed">{f.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-center">
            <h2 className="text-3xl font-heading font-bold text-on-surface sm:text-4xl">How it works</h2>
            <p className="mt-3 text-body-lg text-on-surface-variant">Three steps to a healthier you.</p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-3">
            {[
              {
                step: '01',
                title: 'Create your profile',
                desc: 'Tell us about yourself — age, weight, height, goals, lifestyle habits, and medical conditions.',
              },
              {
                step: '02',
                title: 'Log daily metrics',
                desc: 'Track steps, sleep, water, activity, food, sugar intake and more. Quick-log buttons make it effortless.',
              },
              {
                step: '03',
                title: 'Get personalized insights',
                desc: 'Your health score updates daily. See trends, receive coaching, and understand your risk profile.',
              },
            ].map((s) => (
              <div key={s.step} className="flex flex-col gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-fixed text-on-primary-fixed-variant">
                  <span className="text-headline-md font-bold">{s.step}</span>
                </div>
                <h3 className="text-headline-md font-bold text-on-surface">{s.title}</h3>
                <p className="text-body-md text-on-surface-variant leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <Card className="relative overflow-hidden !bg-primary-fixed px-8 py-14 text-center sm:px-16">
            <div className="pointer-events-none absolute -right-10 -top-10 h-48 w-48 rounded-full bg-primary/10 blur-2xl" />
            <div className="pointer-events-none absolute -bottom-10 -left-10 h-48 w-48 rounded-full bg-tertiary/10 blur-2xl" />
            <h2 className="relative text-3xl font-heading font-bold text-on-primary-fixed sm:text-4xl">
              Start your health journey today
            </h2>
            <p className="relative mt-4 text-body-lg text-on-primary-fixed-variant">
              Join Vitality and take control of your preventive health — completely free.
            </p>
            <div className="relative mt-8 flex flex-wrap items-center justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="px-8 shadow-level-2">
                  Get Started <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg" className="px-8 border-on-primary-fixed-variant text-on-primary-fixed">
                  Log in
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-outline-variant/30 py-8">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-on">
              <Activity className="h-4 w-4" />
            </div>
            <span className="text-label-lg font-heading font-bold text-on-surface-variant">Vitality</span>
          </div>
          <p className="text-body-sm text-on-surface-variant">
            &copy; {new Date().getFullYear()} Vitality. Preventive Healthcare AI.
          </p>
        </div>
      </footer>
    </div>
  )
}
