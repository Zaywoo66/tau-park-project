// src/components/Header.tsx
// Minimalist navigation header. It stays fixed at the top.

export default function Header() {
  return (
    <header className="fixed top-0 w-full z-50 px-6 py-6 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-[#2C4A3B]/10 transition-all">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        
        {/* Логотип + Название */}
        <div className="flex items-center gap-2 cursor-pointer">
          <img 
            src="/images/taupark-icon.png" 
            alt="Логотип TAU PARK" 
            className="h-24 md:h-32 w-auto object-contain -my-6" 
            onError={(e) => {
              // На случай если иконки пока нет, просто скроем её, чтобы не ломать верстку
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          <span className="text-2xl font-serif tracking-[0.15em] uppercase text-[#2C4A3B]">
            Tau Park
          </span>
        </div>
        
        {/* Навигация */}
        <nav className="hidden md:flex gap-10 text-xs uppercase tracking-[0.2em] text-[#2C4A3B]/60 font-semibold">
          <a href="#accommodations" className="hover:text-[#2C4A3B] transition-colors duration-300">Домики</a>
          <a href="#amenities" className="hover:text-[#2C4A3B] transition-colors duration-300">Удобства</a>
          <a href="#contact" className="hover:text-[#2C4A3B] transition-colors duration-300">Контакты</a>
        </nav>

        {/* Кнопка */}
        <button className="border border-[#2C4A3B] px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-[#2C4A3B] hover:bg-[#2C4A3B] hover:text-[#D9C5A0] transition-colors duration-300">
          Забронировать
        </button>
      </div>
    </header>
  );
}