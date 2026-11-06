import {
  Check,
  Copy,
  Fingerprint,
  Plus,
  Search,
  ShoppingCart,
  Trash2,
  Trophy,
  Upload,
  User,
  X,
  Zap,
  type LucideProps,
} from "lucide-react";

export const SearchIcon = (props: LucideProps) => <Search size={14} {...props} />;
export const CartIcon = (props: LucideProps) => <ShoppingCart size={16} {...props} />;
export const TrophyIcon = (props: LucideProps) => <Trophy size={11} {...props} />;
export const BoltIcon = (props: LucideProps) => <Zap size={14} {...props} />;
export const PlusIcon = (props: LucideProps) => <Plus size={14} {...props} />;
export const CheckIcon = (props: LucideProps) => <Check size={14} {...props} />;
export const TrashIcon = (props: LucideProps) => <Trash2 size={13} {...props} />;
export const XIcon = (props: LucideProps) => <X size={18} {...props} />;
export const FingerprintIcon = (props: LucideProps) => <Fingerprint size={14} {...props} />;
export const UserIcon = (props: LucideProps) => <User size={14} {...props} />;
export const CopyIcon = (props: LucideProps) => <Copy size={13} {...props} />;
export const UploadIcon = (props: LucideProps) => <Upload size={28} {...props} />;
