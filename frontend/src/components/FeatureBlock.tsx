const FEATURES = [
  {
    id: 1,
    title: "Больше, Чем Отдых.\nИстинное Погружение.",
    description: "Вдохните кристально чистый свежий воздух и оставьте городскую суету далеко позади. Здесь время замедляет свой ход, оставляя вас наедине с первозданной тишиной и подлинными эмоциями.",
    buttonText: "Ощутить атмосферу",
    image: "/images/feature-experience.jpg",
    imageFirst: true
  },
  {
    id: 2,
    title: "Дикие Тропы.\nЕдинение с Природой.",
    description: "Отправляйтесь на утреннюю конную прогулку по скрытым тропам или исследуйте бескрайние степные просторы пешком. Откройте для себя величественные пейзажи, доступные лишь тем, кто ищет настоящих приключений.",
    buttonText: "Наши маршруты",
    image: "/images/feature-experience-1.jpg",
    imageFirst: false
  },
  {
    id: 3,
    title: "Вечерний Уют.\nБанные Традиции.",
    description: "После насыщенного дня согрейтесь в настоящей бане на дровах. Живой треск поленьев, целебный аромат дикого кедра и душевные беседы у вечернего костра под бескрайним звездным небом.",
    buttonText: "Забронировать баню",
    image: "/images/feature-experience-2.jpg",
    imageFirst: true
  }
];

export default function FeatureBlock() {
  return (
    <section className="py-24 px-4 sm:px-6 max-w-7xl mx-auto space-y-32">
      {FEATURES.map((feature) => (
        <div
          key={feature.id}
          className={`relative flex flex-col ${feature.imageFirst ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center lg:items-end lg:pb-12`}
        >
          {/* Фотография */}
          <div className="w-full lg:w-3/4 aspect-[4/3] lg:aspect-[16/9] overflow-hidden bg-[#2C4A3B]/5">
            <img
              src={feature.image}
              alt={feature.title.replace('\n', ' ')}
              className="w-full h-full object-cover transition-transform duration-1000 hover:scale-105"
            />
          </div>

          {/* Текстовый блок со смещением (Offset Card) */}
          <div
            className={`w-11/12 sm:w-10/12 lg:w-5/12 bg-[#FAF8F5] border border-[#2C4A3B]/10 p-8 md:p-12 lg:p-16 shadow-2xl -mt-16 lg:mt-0 lg:absolute lg:bottom-0 z-10 ${feature.imageFirst ? 'lg:right-4' : 'lg:left-4'
              }`}
          >
            <h2 className="text-3xl md:text-4xl font-serif text-[#2C4A3B] mb-6 leading-tight whitespace-pre-line">
              {feature.title}
            </h2>

            <p className="text-[#2C4A3B]/80 font-light leading-relaxed mb-10 text-base md:text-lg">
              {feature.description}
            </p>

            <button className="bg-transparent border border-[#2C4A3B] text-[#2C4A3B] text-xs font-semibold uppercase tracking-widest px-8 py-4 hover:bg-[#2C4A3B] hover:text-[#FAF8F5] transition-all duration-300 w-full sm:w-auto">
              {feature.buttonText}
            </button>
          </div>
        </div>
      ))}
    </section>
  );
}