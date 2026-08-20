const ACTIVITIES = [
  { id: 1, title: "Термальные Бассейны", image: "/images/activity-pools.jpg" },
  { id: 2, title: "Банные Традиции", image: "/images/activity-sauna.jpg" },
  { id: 3, title: "Уютные Домики", image: "/images/activity-cabins.jpg" },
  { id: 4, title: "Активный Отдых", image: "/images/activity-leisure.jpg" },
];

export default function OverviewGrid() {
  return (
    <section id="amenities" className="py-24 px-6 max-w-7xl mx-auto text-center">
      {/* Текстовый блок */}
      <div className="max-w-3xl mx-auto mb-20">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-serif text-[#2C4A3B] mb-8 tracking-wide">
          Добро пожаловать в Tau Park
        </h2>
        <div className="space-y-6 text-[#2C4A3B]/80 font-light leading-relaxed text-base md:text-lg">
          <p>
            Расположенный в нетронутой степи недалеко от Косшы, TAU PARK предлагает уникальное сочетание первозданной природы и премиального комфорта. Отвлекитесь от городского шума и погрузитесь в атмосферу полного обновления.
          </p>
          <p>
            Расслабляющие термальные бассейны, традиционные дровяные бани и потрясающие живописные просторы ждут вас. Мы продумали всё, чтобы ваш отдых был по-настоящему гармоничным и незабываемым.
          </p>
        </div>
      </div>

      {/* Сетка активностей */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {ACTIVITIES.map((item) => (
          <div 
            key={item.id} 
            className="group relative aspect-[4/3] sm:aspect-square w-full bg-[#2C4A3B]/10 overflow-hidden cursor-pointer"
          >
            {/* Изображение */}
            <img 
              src={item.image} 
              alt={item.title} 
              className="absolute inset-0 w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105"
            />
            
            {/* Оверлей (слегка зеленый) */}
            <div className="absolute inset-0 bg-[#2C4A3B]/30 group-hover:bg-[#2C4A3B]/40 transition-colors duration-500 z-10 mix-blend-multiply" />
            
            {/* Текст */}
            <div className="absolute inset-0 flex items-center justify-center z-20">
              <h3 className="text-[#FAF8F5] text-lg md:text-xl font-serif tracking-[0.15em] uppercase transition-all duration-500 group-hover:-translate-y-1 drop-shadow-md">
                {item.title}
              </h3>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}