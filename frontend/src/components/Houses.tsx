const MOCK_HOUSES = [
  { 
    id: 1, 
    name: "Березовый Домик", 
    price: "45 000 ₸", 
    capacity: "До 4 гостей", 
    description: "Уютное деревянное убежище с панорамными окнами на утренний лес. Идеально для романтического уикенда, где только пение птиц нарушает первозданную тишину.",
    image: "/images/house-birch.jpg" 
  },
  { 
    id: 2, 
    name: "Кедровая Вилла", 
    price: "80 000 ₸", 
    capacity: "До 10 гостей", 
    description: "Просторное шале, пропитанное терпким ароматом дикого кедра. Огромная терраса создана для теплых бесед под бескрайним звездным небом.",
    image: "/images/house-cedar.jpg" 
  },
  { 
    id: 3, 
    name: "Сосновый Коттедж", 
    price: "120 000 ₸", 
    capacity: "До 20 гостей", 
    description: "Флагманская резиденция для больших компаний. Величественные вековые сосны вокруг и живой огонь в гостиной станут центром ваших незабываемых историй.",
    image: "/images/house-pine.jpg" 
  },
];

export default function Houses() {
  return (
    <section id="accommodations" className="py-24 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-20">
        <h2 className="text-4xl md:text-5xl font-serif mb-4 text-[#2C4A3B]">Наши Домики</h2>
        <p className="text-sm tracking-[0.2em] uppercase text-[#2C4A3B]/60 font-semibold">
          Выберите свое место силы
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 lg:gap-8">
        {MOCK_HOUSES.map((house) => (
          <article key={house.id} className="group cursor-pointer flex flex-col relative pb-4">
            {/* Фотография */}
            <div className="w-full aspect-[4/3] bg-[#2C4A3B]/5 overflow-hidden">
               <img 
                 src={house.image} 
                 alt={house.name} 
                 className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105"
               />
            </div>

            {/* Карточка с информацией (Offset Layout) */}
            <div className="w-11/12 mx-auto bg-[#FAF8F5] border border-[#2C4A3B]/10 p-6 shadow-xl -mt-16 relative z-10 flex flex-col transition-transform duration-300 group-hover:-translate-y-1">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2 gap-2">
                <h3 className="text-2xl font-serif text-[#2C4A3B] leading-none">
                  {house.name}
                </h3>
                <span className="text-sm font-bold text-[#2C4A3B] whitespace-nowrap">
                  от {house.price}
                </span>
              </div>
              
              <p className="text-xs uppercase tracking-widest text-[#2C4A3B]/70 mb-4 font-semibold">
                {house.capacity}
              </p>
              
              <p className="text-sm text-[#2C4A3B]/80 font-light leading-relaxed">
                {house.description}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}