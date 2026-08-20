export default function Hero() {
  return (
    <section 
      className="relative h-screen w-full flex flex-col justify-center items-center px-4 pt-20 bg-[url('/images/hero-bg.webp')] bg-cover bg-center bg-no-repeat bg-fixed"
    >
      {/* Затемняющий оверлей для читаемости текста */}
      <div className="absolute inset-0 bg-[#2C4A3B]/40 -z-0 mix-blend-multiply" />
      <div className="absolute inset-0 bg-black/30 -z-0" />

      <div className="relative z-10 text-center text-[#D9C5A0] max-w-4xl px-4">
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-serif mb-6 tracking-tight drop-shadow-lg">
          Дыхание Природы
        </h1>
        <p className="text-lg md:text-2xl font-light tracking-wide mb-10 max-w-2xl mx-auto text-white/90 drop-shadow-md">
          Ощутите абсолютную гармонию и найдите уединение в нашем глэмпинге посреди бескрайней степи, вдали от городской суеты.
        </p>
      </div>
    </section>
  );
}