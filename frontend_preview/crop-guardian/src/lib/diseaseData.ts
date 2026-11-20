import type { CropId, DiseaseDetail, DiseaseSummary, Lang } from '../types/api'

/**
 * DEMO KNOWLEDGE BASE.
 * Plain-language reference text used only in demo mode so the Disease Guide can be previewed.
 * In live mode the same screens are filled by GET /api/diseases from the backend RAG knowledge source.
 * It deliberately contains no pesticide names, doses or treatment instructions.
 */

type L = { en: string; bn: string }
const l = (en: string, bn: string): L => ({ en, bn })

interface RawDisease {
  id: string
  crop: CropId
  name: string
  isHealthy: boolean
  overview: L
  symptoms: L[]
  causes: L[]
  prevention: L[]
  management: L[]
}

// ---- shared items -------------------------------------------------------
const OFFICER = l(
  'Ask a local agricultural officer before using any pesticide.',
  'কোনো কীটনাশক বা ছত্রাকনাশক ব্যবহারের আগে স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।',
)
const ROTATE = l(
  'Rotate crops. Do not plant potato or tomato in the same plot year after year.',
  'ফসল পালাবদল করুন। একই জমিতে বছরের পর বছর আলু বা টমেটো লাগাবেন না।',
)
const RESIDUE = l(
  'After harvest, clear and destroy old plant residue.',
  'ফসল তোলার পর পুরোনো গাছের অবশিষ্টাংশ সরিয়ে নষ্ট করুন।',
)
const SPACE = l(
  'Give plants enough space so air can move between them.',
  'গাছের মাঝে পর্যাপ্ত দূরত্ব রাখুন, যাতে বাতাস চলাচল করতে পারে।',
)
const BASE_WATER = l(
  'Water at the base of plants, early in the day, and avoid wetting the leaves.',
  'সকাল সকাল গাছের গোড়ায় পানি দিন এবং পাতা ভেজানো এড়িয়ে চলুন।',
)
const NOT_WET = l(
  'Avoid walking through or working in the field while the leaves are wet.',
  'পাতা ভেজা থাকলে জমিতে হাঁটাহাঁটি বা কাজ করা এড়িয়ে চলুন।',
)
const REMOVE_LEAVES = l(
  'Remove the most affected leaves and destroy them away from the field.',
  'বেশি আক্রান্ত পাতা তুলে জমি থেকে দূরে নষ্ট করুন।',
)
const CLEAN_SEED = l(
  'Use clean, healthy seed or seedlings.',
  'পরিষ্কার ও সুস্থ বীজ বা চারা ব্যবহার করুন।',
)
const WET_LEAVES = l(
  'Leaves staying wet for a long time after rain, dew or irrigation.',
  'বৃষ্টি, শিশির বা সেচের পর পাতা দীর্ঘ সময় ভেজা থাকা।',
)
const KEEP_CHECKING = l(
  'Check your leaves every few days and take a new photo if you see new spots.',
  'কয়েক দিন পরপর পাতা দেখুন এবং নতুন দাগ দেখলে আবার ছবি তুলুন।',
)

const RAW: RawDisease[] = [
  {
    id: 'potato-early-blight',
    crop: 'potato',
    name: 'Early Blight',
    isHealthy: false,
    overview: l(
      'A fungal leaf disease that usually starts on older, lower leaves and slowly spreads upward.',
      'এটি ছত্রাকজনিত পাতার রোগ, যা সাধারণত নিচের পুরোনো পাতায় শুরু হয় এবং ধীরে ধীরে উপরের দিকে ছড়ায়।',
    ),
    symptoms: [
      l('Dark brown spots with ring-like patterns, like a target.', 'গাঢ় বাদামি দাগ, যার ভেতরে গোল গোল রেখা দেখা যায়।'),
      l('A yellow area around the spots.', 'দাগের চারপাশে হলুদ ভাব।'),
      l('Badly affected leaves dry out and fall.', 'বেশি আক্রান্ত পাতা শুকিয়ে ঝরে পড়ে।'),
    ],
    causes: [
      l('Warm weather with dry spells followed by dew or rain.', 'উষ্ণ আবহাওয়া, যেখানে শুকনো সময়ের পর শিশির বা বৃষ্টি আসে।'),
      WET_LEAVES,
      l('Weak or underfed plants.', 'দুর্বল বা সারের অভাবে থাকা গাছ।'),
      l('Infected plant residue left from earlier crops.', 'আগের ফসলের আক্রান্ত অবশিষ্টাংশ জমিতে থেকে যাওয়া।'),
    ],
    prevention: [ROTATE, RESIDUE, l('Feed plants in a balanced way.', 'সুষম সার দিন।'), l('Use healthy, good-quality seed tubers.', 'সুস্থ ও ভালো মানের বীজ আলু ব্যবহার করুন।')],
    management: [REMOVE_LEAVES, NOT_WET, BASE_WATER, OFFICER],
  },
  {
    id: 'potato-late-blight',
    crop: 'potato',
    name: 'Late Blight',
    isHealthy: false,
    overview: l(
      'A fast-spreading disease that can damage leaves, stems and even tubers, especially in cool, humid, cloudy weather.',
      'এটি দ্রুত ছড়িয়ে পড়া রোগ, যা পাতা, ডগা এমনকি আলুরও ক্ষতি করতে পারে; ঠান্ডা, আর্দ্র ও মেঘলা আবহাওয়ায় বেশি দেখা যায়।',
    ),
    symptoms: [
      l('Dark, water-soaked patches on leaves that grow quickly.', 'পাতায় ভেজা ভেজা গাঢ় দাগ, যা দ্রুত বড় হয়।'),
      l('White, fuzzy growth under the leaf on damp mornings.', 'ভেজা সকালে পাতার নিচে সাদা তুলার মতো আস্তর।'),
      l('Stems may turn dark and plants can collapse.', 'ডগা কালচে হয়ে গাছ নেতিয়ে পড়তে পারে।'),
      l('Tubers can show firm, dark, sunken patches.', 'আলুর গায়ে শক্ত, কালচে, দেবে যাওয়া দাগ দেখা দিতে পারে।'),
    ],
    causes: [
      l('Cool, humid and cloudy weather with long wet periods.', 'ঠান্ডা, আর্দ্র ও মেঘলা আবহাওয়া এবং দীর্ঘ সময় ভেজা থাকা।'),
      l('Spores carried by wind and rain from nearby infected plants.', 'আশপাশের আক্রান্ত গাছ থেকে বাতাস ও বৃষ্টিতে ছড়ানো রেণু।'),
      l('Infected seed tubers or leftover potatoes from earlier crops.', 'আক্রান্ত বীজ আলু বা আগের ফসলের ফেলে রাখা আলু।'),
    ],
    prevention: [
      l('Use healthy seed tubers.', 'সুস্থ বীজ আলু ব্যবহার করুন।'),
      SPACE,
      l('Remove leftover or self-grown potatoes from the field.', 'জমিতে ফেলে রাখা বা নিজে থেকে গজানো আলু সরিয়ে ফেলুন।'),
      l('Look at your leaves more often when the weather is cool and damp.', 'আবহাওয়া ঠান্ডা ও ভেজা থাকলে পাতা আরও ঘন ঘন দেখুন।'),
    ],
    management: [
      l('Act quickly. Remove infected plants and destroy them away from the field.', 'দ্রুত ব্যবস্থা নিন। আক্রান্ত গাছ তুলে জমি থেকে দূরে নষ্ট করুন।'),
      l('Do not store tubers from affected plants together with healthy ones.', 'আক্রান্ত গাছের আলু সুস্থ আলুর সাথে মজুত করবেন না।'),
      l('Tell neighbouring farmers and your agricultural officer, because it spreads fast.', 'প্রতিবেশী কৃষক ও কৃষি কর্মকর্তাকে জানান, কারণ রোগটি দ্রুত ছড়ায়।'),
      OFFICER,
    ],
  },
  {
    id: 'potato-healthy',
    crop: 'potato',
    name: 'Healthy',
    isHealthy: true,
    overview: l(
      'The leaf looks healthy. Good, regular care helps it stay that way.',
      'পাতাটি সুস্থ দেখাচ্ছে। নিয়মিত ভালো যত্ন নিলে তা সুস্থ থাকবে।',
    ),
    symptoms: [
      l('Leaves are an even green colour.', 'পাতার রং সমান সবুজ।'),
      l('No spots, patches or mold.', 'কোনো দাগ, ছোপ বা ছত্রাক নেই।'),
      l('New growth looks fresh and firm.', 'নতুন পাতা সতেজ ও শক্ত।'),
    ],
    causes: [],
    prevention: [ROTATE, RESIDUE, l('Keep weeds under control.', 'আগাছা নিয়ন্ত্রণে রাখুন।')],
    management: [
      KEEP_CHECKING,
      l('Water regularly without letting the field stay waterlogged.', 'নিয়মিত সেচ দিন, তবে জমিতে পানি জমে থাকতে দেবেন না।'),
      l('Feed plants in a balanced way, following local advice.', 'স্থানীয় পরামর্শ অনুযায়ী সুষম সার দিন।'),
    ],
  },
  {
    id: 'tomato-bacterial-spot',
    crop: 'tomato',
    name: 'Bacterial Spot',
    isHealthy: false,
    overview: l(
      'A bacterial disease that causes small spots on leaves and fruit. It is worse in warm, wet weather.',
      'এটি ব্যাকটেরিয়াজনিত রোগ, যাতে পাতা ও ফলে ছোট ছোট দাগ পড়ে। উষ্ণ ও ভেজা আবহাওয়ায় এটি বেশি হয়।',
    ),
    symptoms: [
      l('Small, dark, slightly greasy-looking spots on leaves.', 'পাতায় ছোট, গাঢ়, কিছুটা তেলতেলে দাগ।'),
      l('Spots may have a yellow edge, and the centre can dry and tear.', 'দাগের কিনারা হলুদ হতে পারে এবং মাঝখান শুকিয়ে ছিঁড়ে যেতে পারে।'),
      l('Rough, raised, scabby spots on fruit.', 'ফলে খসখসে, উঁচু, খোসার মতো দাগ।'),
    ],
    causes: [
      l('Infected seed or seedlings.', 'আক্রান্ত বীজ বা চারা।'),
      l('Rain, irrigation water and handling that carry bacteria from leaf to leaf.', 'বৃষ্টি, সেচের পানি ও হাতের ছোঁয়ায় ব্যাকটেরিয়া এক পাতা থেকে আরেক পাতায় ছড়ায়।'),
      l('Warm, humid weather.', 'উষ্ণ ও আর্দ্র আবহাওয়া।'),
    ],
    prevention: [CLEAN_SEED, ROTATE, l('Avoid touching plants while they are wet.', 'গাছ ভেজা থাকলে ছোঁয়া বা কাজ করা এড়িয়ে চলুন।'), l('Wash tools and hands between plots.', 'এক জমি থেকে আরেক জমিতে যাওয়ার আগে যন্ত্রপাতি ও হাত ধুয়ে নিন।')],
    management: [REMOVE_LEAVES, BASE_WATER, NOT_WET, OFFICER],
  },
  {
    id: 'tomato-early-blight',
    crop: 'tomato',
    name: 'Early Blight',
    isHealthy: false,
    overview: l(
      'A fungal disease that usually starts on the lower, older leaves and can also reach stems and fruit.',
      'এটি ছত্রাকজনিত রোগ, যা সাধারণত নিচের পুরোনো পাতায় শুরু হয় এবং ডাল ও ফলেও ছড়াতে পারে।',
    ),
    symptoms: [
      l('Brown spots with ring-like patterns, like a target.', 'বাদামি দাগ, যার ভেতরে গোল গোল রেখা দেখা যায়।'),
      l('A yellow area around the spots; badly affected leaves dry and fall.', 'দাগের চারপাশে হলুদ ভাব; বেশি আক্রান্ত পাতা শুকিয়ে ঝরে পড়ে।'),
      l('Dark, sunken spots near the fruit stalk.', 'ফলের বোঁটার কাছে গাঢ়, দেবে যাওয়া দাগ।'),
    ],
    causes: [
      l('Warm weather with alternating wet and dry periods.', 'উষ্ণ আবহাওয়া, যেখানে ভেজা ও শুকনো সময় পালা করে আসে।'),
      WET_LEAVES,
      l('Plants weakened by lack of nutrition or heavy fruit load.', 'পুষ্টির অভাব বা বেশি ফলের চাপে দুর্বল গাছ।'),
      l('Infected plant residue left in the soil.', 'মাটিতে থেকে যাওয়া আক্রান্ত গাছের অবশিষ্টাংশ।'),
    ],
    prevention: [ROTATE, RESIDUE, SPACE, l('Stake plants so leaves stay off the soil.', 'খুঁটি দিয়ে গাছ বাঁধুন, যাতে পাতা মাটি না ছোঁয়।')],
    management: [REMOVE_LEAVES, NOT_WET, BASE_WATER, OFFICER],
  },
  {
    id: 'tomato-late-blight',
    crop: 'tomato',
    name: 'Late Blight',
    isHealthy: false,
    overview: l(
      'A fast-spreading disease of leaves, stems and fruit that thrives in cool, wet, cloudy weather.',
      'এটি পাতা, ডাল ও ফলের দ্রুত ছড়ানো রোগ, যা ঠান্ডা, ভেজা ও মেঘলা আবহাওয়ায় বেশি হয়।',
    ),
    symptoms: [
      l('Large, greasy-looking grey-green to brown patches on leaves.', 'পাতায় বড়, তেলতেলে, ধূসর-সবুজ থেকে বাদামি দাগ।'),
      l('White, fuzzy growth under leaves in damp conditions.', 'ভেজা অবস্থায় পাতার নিচে সাদা তুলার মতো আস্তর।'),
      l('Dark, firm patches on fruit.', 'ফলে গাঢ়, শক্ত দাগ।'),
    ],
    causes: [
      l('Cool, humid and cloudy weather with long wet periods.', 'ঠান্ডা, আর্দ্র ও মেঘলা আবহাওয়া এবং দীর্ঘ সময় ভেজা থাকা।'),
      l('Spores carried by wind and rain from nearby tomato or potato plants.', 'আশপাশের টমেটো বা আলু গাছ থেকে বাতাস ও বৃষ্টিতে ছড়ানো রেণু।'),
    ],
    prevention: [SPACE, ROTATE, RESIDUE, l('Look at your leaves more often when the weather is cool and damp.', 'আবহাওয়া ঠান্ডা ও ভেজা থাকলে পাতা আরও ঘন ঘন দেখুন।')],
    management: [
      l('Act quickly. Remove infected plants and destroy them away from the field.', 'দ্রুত ব্যবস্থা নিন। আক্রান্ত গাছ তুলে জমি থেকে দূরে নষ্ট করুন।'),
      NOT_WET,
      l('Tell neighbouring farmers and your agricultural officer, because it spreads fast.', 'প্রতিবেশী কৃষক ও কৃষি কর্মকর্তাকে জানান, কারণ রোগটি দ্রুত ছড়ায়।'),
      OFFICER,
    ],
  },
  {
    id: 'tomato-leaf-mold',
    crop: 'tomato',
    name: 'Leaf Mold',
    isHealthy: false,
    overview: l(
      'A fungal disease that likes very humid air, especially where plants are crowded or air hardly moves.',
      'এটি ছত্রাকজনিত রোগ, যা খুব আর্দ্র বাতাস পছন্দ করে, বিশেষ করে যেখানে গাছ ঘন বা বাতাস চলাচল কম।',
    ),
    symptoms: [
      l('Pale green or yellow spots on the upper side of leaves.', 'পাতার উপরের দিকে ফ্যাকাশে সবুজ বা হলুদ দাগ।'),
      l('Olive-green to grey-brown, velvety mold on the underside.', 'পাতার নিচের দিকে জলপাই-সবুজ থেকে ধূসর-বাদামি মখমলের মতো ছত্রাক।'),
      l('In bad cases, leaves curl, dry and fall.', 'বেশি হলে পাতা কুঁকড়ে শুকিয়ে ঝরে পড়ে।'),
    ],
    causes: [
      l('Very humid air for long periods.', 'দীর্ঘ সময় ধরে খুব আর্দ্র বাতাস।'),
      l('Crowded plants or covered growing spaces with little air movement.', 'ঘন গাছ বা ঢাকা জায়গায় বাতাস চলাচল কম।'),
      WET_LEAVES,
    ],
    prevention: [SPACE, l('Stake and prune so air can pass through the plants.', 'খুঁটি ও ডাল ছাঁটাই করে গাছের ভেতরে বাতাস চলাচলের ব্যবস্থা করুন।'), BASE_WATER, RESIDUE],
    management: [REMOVE_LEAVES, l('Improve air movement around the plants.', 'গাছের চারপাশে বাতাস চলাচল বাড়ান।'), BASE_WATER, OFFICER],
  },
  {
    id: 'tomato-septoria-leaf-spot',
    crop: 'tomato',
    name: 'Septoria Leaf Spot',
    isHealthy: false,
    overview: l(
      'A fungal disease that causes many small spots, usually starting on the lowest leaves.',
      'এটি ছত্রাকজনিত রোগ, যাতে অনেক ছোট ছোট দাগ পড়ে এবং সাধারণত সবচেয়ে নিচের পাতায় শুরু হয়।',
    ),
    symptoms: [
      l('Many small round spots with dark edges and pale grey centres.', 'অনেক ছোট গোল দাগ, কিনারা গাঢ় ও মাঝখান ফ্যাকাশে ধূসর।'),
      l('Tiny dark dots may be visible in the middle of the spots.', 'দাগের মাঝখানে ছোট কালো ফোঁটা দেখা যেতে পারে।'),
      l('Lower leaves turn yellow and fall, and the problem moves upward.', 'নিচের পাতা হলুদ হয়ে ঝরে পড়ে এবং সমস্যা ধীরে ধীরে উপরে ওঠে।'),
    ],
    causes: [
      WET_LEAVES,
      l('Spores splashing from soil or old plant debris onto lower leaves.', 'মাটি বা পুরোনো আবর্জনা থেকে রেণু ছিটকে নিচের পাতায় লাগে।'),
      l('Warm, humid weather.', 'উষ্ণ ও আর্দ্র আবহাওয়া।'),
    ],
    prevention: [ROTATE, RESIDUE, l('Mulch or stake so leaves do not touch the soil.', 'মালচ বা খুঁটি দিন, যাতে পাতা মাটি না ছোঁয়।'), BASE_WATER],
    management: [REMOVE_LEAVES, NOT_WET, SPACE, OFFICER],
  },
  {
    id: 'tomato-spider-mites',
    crop: 'tomato',
    name: 'Spider Mites',
    isHealthy: false,
    overview: l(
      'Tiny pests (not a fungus or a virus) that suck sap from the underside of leaves. They are most active in hot, dry weather.',
      'এগুলো খুব ছোট পোকা (ছত্রাক বা ভাইরাস নয়), যারা পাতার নিচ থেকে রস চুষে খায়। গরম ও শুকনো আবহাওয়ায় এরা বেশি সক্রিয়।',
    ),
    symptoms: [
      l('Tiny pale or yellow dots on leaves.', 'পাতায় ছোট ফ্যাকাশে বা হলুদ ফোঁটা।'),
      l('Fine webbing under leaves or between stems.', 'পাতার নিচে বা ডালের মাঝে সূক্ষ্ম জাল।'),
      l('Leaves turn bronze or dry out and may fall.', 'পাতা তামাটে হয় বা শুকিয়ে ঝরে পড়তে পারে।'),
    ],
    causes: [
      l('Hot, dry weather.', 'গরম ও শুকনো আবহাওয়া।'),
      l('Dusty conditions around the plants.', 'গাছের আশপাশে ধুলাবালি।'),
      l('Plants stressed by lack of water.', 'পানির অভাবে চাপে থাকা গাছ।'),
    ],
    prevention: [
      l('Look at the underside of leaves regularly.', 'নিয়মিত পাতার নিচের দিক দেখুন।'),
      l('Keep plants well watered and reduce dust where you can.', 'গাছে ঠিকমতো পানি দিন এবং সম্ভব হলে ধুলা কমান।'),
      l('Keep weeds down, as mites can live on them.', 'আগাছা কম রাখুন, কারণ এতে মাকড় থাকতে পারে।'),
    ],
    management: [
      l('Remove heavily infested leaves.', 'বেশি আক্রান্ত পাতা সরিয়ে ফেলুন।'),
      l('On a small planting, a gentle spray of plain water under the leaves can reduce mites.', 'ছোট আকারের চাষে পাতার নিচে হালকা করে সাধারণ পানি ছিটালে মাকড় কমতে পারে।'),
      l('Ask an agricultural officer before using any pesticide, because some products also harm helpful insects.', 'কোনো কীটনাশক ব্যবহারের আগে কৃষি কর্মকর্তার পরামর্শ নিন, কারণ কিছু ওষুধ উপকারী পোকারও ক্ষতি করে।'),
    ],
  },
  {
    id: 'tomato-target-spot',
    crop: 'tomato',
    name: 'Target Spot',
    isHealthy: false,
    overview: l(
      'A fungal disease that makes brown, ring-patterned spots on leaves and sometimes on stems and fruit.',
      'এটি ছত্রাকজনিত রোগ, যাতে পাতায় এবং কখনো কখনো ডাল ও ফলে বাদামি, গোল রেখাযুক্ত দাগ পড়ে।',
    ),
    symptoms: [
      l('Brown spots with ring-like patterns and a yellow edge.', 'বাদামি দাগ, যার ভেতরে গোল গোল রেখা ও কিনারায় হলুদ ভাব।'),
      l('Spots can also appear on stems and fruit.', 'ডাল ও ফলেও দাগ দেখা দিতে পারে।'),
      l('Leaves may drop, leaving fruit exposed to the sun.', 'পাতা ঝরে গেলে ফল রোদে খোলা পড়ে যেতে পারে।'),
    ],
    causes: [
      l('Warm, humid weather with long leaf wetness.', 'উষ্ণ ও আর্দ্র আবহাওয়া এবং পাতা দীর্ঘ সময় ভেজা থাকা।'),
      l('Dense plant growth with poor airflow.', 'ঘন গাছ এবং কম বাতাস চলাচল।'),
      l('Infected plant residue from earlier crops.', 'আগের ফসলের আক্রান্ত অবশিষ্টাংশ।'),
    ],
    prevention: [ROTATE, RESIDUE, SPACE, BASE_WATER],
    management: [REMOVE_LEAVES, NOT_WET, l('Improve air movement around the plants.', 'গাছের চারপাশে বাতাস চলাচল বাড়ান।'), OFFICER],
  },
  {
    id: 'tomato-yellow-leaf-curl-virus',
    crop: 'tomato',
    name: 'Tomato Yellow Leaf Curl Virus',
    isHealthy: false,
    overview: l(
      'A virus spread by whiteflies. Once a plant is infected it cannot be cured.',
      'এটি সাদা মাছির মাধ্যমে ছড়ানো ভাইরাস। একবার আক্রান্ত হলে গাছ আর সারানো যায় না।',
    ),
    symptoms: [
      l('Leaves curl upward and become small and thick.', 'পাতা উপরের দিকে কুঁকড়ে যায় এবং ছোট ও মোটা হয়।'),
      l('Yellow leaf edges.', 'পাতার কিনারা হলুদ।'),
      l('Plants stay short, with few flowers and little fruit.', 'গাছ খাটো থাকে, ফুল ও ফল কম হয়।'),
    ],
    causes: [
      l('Whiteflies carrying the virus from infected plants.', 'আক্রান্ত গাছ থেকে ভাইরাস বহনকারী সাদা মাছি।'),
      l('Infected seedlings brought into the field.', 'জমিতে আনা আক্রান্ত চারা।'),
      l('Weeds and nearby crops that keep whiteflies around.', 'আগাছা ও আশপাশের ফসল, যেখানে সাদা মাছি থাকে।'),
    ],
    prevention: [
      l('Check seedlings for whiteflies before planting.', 'রোপণের আগে চারায় সাদা মাছি আছে কিনা দেখুন।'),
      l('Use fine insect-proof net over the seedbed.', 'চারা তলায় সূক্ষ্ম পোকা-রোধী জাল ব্যবহার করুন।'),
      l('Keep weeds down around the field.', 'জমির চারপাশে আগাছা কম রাখুন।'),
      l('Ask your agricultural officer about tolerant varieties.', 'সহনশীল জাতের বিষয়ে কৃষি কর্মকর্তার কাছে জানুন।'),
    ],
    management: [
      l('Remove and destroy infected plants early to protect healthy ones.', 'সুস্থ গাছ বাঁচাতে আক্রান্ত গাছ আগেভাগে তুলে নষ্ট করুন।'),
      l('Reduce whiteflies. Ask an officer about safe ways to control them.', 'সাদা মাছি কমান। নিরাপদ নিয়ন্ত্রণের উপায় কৃষি কর্মকর্তার কাছে জানুন।'),
      l('No medicine can cure a plant that already has the virus.', 'ভাইরাসে আক্রান্ত গাছ সারানোর মতো কোনো ওষুধ নেই।'),
    ],
  },
  {
    id: 'tomato-mosaic-virus',
    crop: 'tomato',
    name: 'Tomato Mosaic Virus',
    isHealthy: false,
    overview: l(
      'A virus that spreads easily by touch, through hands, tools and clothing, and sometimes through seed.',
      'এটি ভাইরাস, যা হাত, যন্ত্রপাতি ও কাপড়ের ছোঁয়ায় সহজে ছড়ায় এবং কখনো কখনো বীজের মাধ্যমেও ছড়ায়।',
    ),
    symptoms: [
      l('Light and dark green mottling on leaves, like a patchwork.', 'পাতায় হালকা ও গাঢ় সবুজ ছোপ, যেন তালি দেওয়া।'),
      l('Leaves may look thin, twisted or fern-like.', 'পাতা সরু, মোচড়ানো বা ফার্নের মতো দেখাতে পারে।'),
      l('Slow growth and lower fruit quality.', 'বাড়ন্ত ধীর এবং ফলের মান কম।'),
    ],
    causes: [
      l('Touching infected plants and then healthy ones.', 'আক্রান্ত গাছ ছুঁয়ে সুস্থ গাছ ছোঁয়া।'),
      l('Contaminated tools, hands and stakes.', 'দূষিত যন্ত্রপাতি, হাত ও খুঁটি।'),
      l('Infected seed or old plant debris.', 'আক্রান্ত বীজ বা পুরোনো গাছের আবর্জনা।'),
    ],
    prevention: [
      l('Wash hands with soap before handling plants.', 'গাছে হাত দেওয়ার আগে সাবান দিয়ে হাত ধুয়ে নিন।'),
      l('Clean tools and stakes before reusing them.', 'যন্ত্রপাতি ও খুঁটি আবার ব্যবহারের আগে পরিষ্কার করুন।'),
      CLEAN_SEED,
      RESIDUE,
    ],
    management: [
      l('Carefully remove and destroy infected plants.', 'সাবধানে আক্রান্ত গাছ তুলে নষ্ট করুন।'),
      l('Handle healthy plants first and suspect plants last.', 'আগে সুস্থ গাছের কাজ করুন, সন্দেহজনক গাছের কাজ সবার শেষে।'),
      l('No medicine can cure a virus. Ask your agricultural officer for advice.', 'ভাইরাস সারানোর মতো কোনো ওষুধ নেই। পরামর্শের জন্য কৃষি কর্মকর্তার সাথে কথা বলুন।'),
    ],
  },
  {
    id: 'tomato-healthy',
    crop: 'tomato',
    name: 'Healthy',
    isHealthy: true,
    overview: l(
      'The leaf looks healthy. Good, regular care helps it stay that way.',
      'পাতাটি সুস্থ দেখাচ্ছে। নিয়মিত ভালো যত্ন নিলে তা সুস্থ থাকবে।',
    ),
    symptoms: [
      l('Leaves are an even green colour.', 'পাতার রং সমান সবুজ।'),
      l('No spots, patches, webbing or mold.', 'কোনো দাগ, ছোপ, জাল বা ছত্রাক নেই।'),
      l('New growth looks fresh and firm.', 'নতুন পাতা সতেজ ও শক্ত।'),
    ],
    causes: [],
    prevention: [ROTATE, SPACE, BASE_WATER],
    management: [
      KEEP_CHECKING,
      l('Stake plants so leaves stay off the soil.', 'খুঁটি দিয়ে গাছ বাঁধুন, যাতে পাতা মাটি না ছোঁয়।'),
      l('Feed plants in a balanced way, following local advice.', 'স্থানীয় পরামর্শ অনুযায়ী সুষম সার দিন।'),
    ],
  },
]

const pick = (items: L[], lang: Lang) => items.map((i) => i[lang])

export const DISEASE_IDS = RAW.map((d) => d.id)

export function getRaw(id: string) {
  return RAW.find((d) => d.id === id)
}

export function cropHealthyId(crop: CropId): string | null {
  return crop === 'potato' ? 'potato-healthy' : crop === 'tomato' ? 'tomato-healthy' : null
}

export function summaries(lang: Lang, crop?: CropId, q?: string): DiseaseSummary[] {
  const needle = (q ?? '').trim().toLowerCase()
  return RAW.filter((d) => (!crop || d.crop === crop) && (!needle || d.name.toLowerCase().includes(needle)))
    .map((d) => ({
      id: d.id,
      crop: d.crop,
      name: d.name,
      isHealthy: d.isHealthy,
      blurb: d.overview[lang],
    }))
}

export function detail(id: string, lang: Lang): DiseaseDetail | null {
  const d = getRaw(id)
  if (!d) return null
  return {
    id: d.id,
    crop: d.crop,
    name: d.name,
    isHealthy: d.isHealthy,
    blurb: d.overview[lang],
    overview: d.overview[lang],
    symptoms: pick(d.symptoms, lang),
    causes: pick(d.causes, lang),
    prevention: pick(d.prevention, lang),
    management: pick(d.management, lang),
    // Demo mode never invents medicine data. The UI shows the "no verified information" message.
    treatment: { verified: false, products: [] },
  }
}
