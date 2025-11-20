export interface Owner {
  id: string;
  name: string;
  email: string;
  phone: string;
}

export interface OwnerCreateData {
  name: string;
  email: string;
  phone: string;
}

export interface OwnerListProps {
  fetchTrigger: number;
}

export interface OwnerFormProps {
  onOwnerCreated: () => void;
}

export interface FastAPIError {
  detail: string | any[] | object;
}

export interface Asset {
  id: string;
  name: string;
  category: string;
  owner_id: string;
  owner_ref?: Owner; 
}

export interface AssetCreateData {
  name: string;
  category: string;
  owner_id: string; 
}

export interface AssetListProps {
  fetchTrigger: number;
}

export interface AssetFormProps {
  onAssetCreated: () => void;
}

export interface BaseFormProps {
    onSubmitted?: () => void; 
}