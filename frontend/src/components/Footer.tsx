// src/components/Footer.tsx
// Minimalist footer component matching the premium pine green / beige aesthetic.

export default function Footer() {
  return (
    <footer className="bg-[#FAF8F5] border-t border-[#2C4A3B]/10 py-16 px-6">
      <div className="max-w-7xl mx-auto flex flex-col items-center">
        {/* Logo */}
        <div className="mb-8 text-center flex flex-col items-center">
          <img 
            src="/images/taupark-icon.png" 
            alt="Логотип TAU PARK" 
            className="h-32 md:h-48 w-auto object-contain opacity-90 mb-2 -mt-8"
            onError={(e) => {
              // Fallback to text if icon is missing
              (e.target as HTMLImageElement).style.display = 'none';
              (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
            }}
          />
          <span className="hidden text-2xl font-serif tracking-widest uppercase text-[#2C4A3B]">
            Tau Park
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-wrap justify-center gap-8 text-xs uppercase tracking-[0.2em] font-semibold text-[#2C4A3B]/70 mb-12">
          <a href="#accommodations" className="hover:text-[#2C4A3B] transition-colors duration-300">Домики</a>
          <a href="#amenities" className="hover:text-[#2C4A3B] transition-colors duration-300">Удобства</a>
          <a href="#contact" className="hover:text-[#2C4A3B] transition-colors duration-300">Контакты</a>
        </nav>

        {/* Contact Info */}
        <div className="text-center text-[#2C4A3B]/80 font-light text-sm space-y-2 mb-12">
          <p>Косшы</p>
          <p><a href="tel:+132446" className="hover:text-[#2C4A3B] transition-colors">+132446</a></p>
          <p><a href="mailto:hello@taupark.kz" className="hover:text-[#2C4A3B] transition-colors">hello@taupark.kz</a></p>
        </div>

        {/* Copyright */}
        <div className="text-xs text-[#2C4A3B]/40 tracking-wider">
          © {new Date().getFullYear()} TAU PARK. Все права защищены.
        </div>
      </div>
    </footer>
  );
}
