export const PACKAGES = {
  S: {
    id: "S",
    name: "Lite Office",
    nameTh: "ไลท์ ออฟฟิศ",
    price: 2900,
    routinePerMonth: 4,
    visitsPerWeek: 1,
    combo: null,
  },
  M: {
    id: "M",
    name: "Growth Office",
    nameTh: "โกรท ออฟฟิศ",
    price: 6900,
    routinePerMonth: 8,
    visitsPerWeek: 2,
    combo: "combo_mini_deep",
  },
  L: {
    id: "L",
    name: "Premium Executive",
    nameTh: "พรีเมียม",
    price: 9900,
    routinePerMonth: 12,
    visitsPerWeek: 3,
    combo: "combo_full_big",
  },
};

export const HIRE_THRESHOLDS = {
  L: 2,
  M: 3,
  S: 6,
  revenueMin: 17000,
};

export const JOB_TYPES = {
  ROUTINE: "routine",
  COMBO_MINI: "combo_mini_deep",
  COMBO_FULL: "combo_full_big",
};
