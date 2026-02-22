'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Settings, Check, Loader } from 'lucide-react';

interface WiFiConfig {
  router_type: string;
  router_url: string;
  router_username: string;
  dns_log_source: string;
  is_enabled: boolean;
}

interface NetworkPolicy {
  id: string;
  name: string;
  description: string;
  block_categories: string[];
  is_active: boolean;
}

const DOMAIN_CATEGORIES = [
  { value: 'social', label: '🔵 Social Media' },
  { value: 'streaming', label: '🎬 Video Streaming' },
  { value: 'adult', label: '⛔ Adult Content' },
  { value: 'gambling', label: '🎰 Gambling' },
  { value: 'malware', label: '🚨 Malware/Phishing' }
];

const ROUTER_OPTIONS = [
  { value: 'unifi', label: '🌐 Ubiquiti UniFi' },
  { value: 'meraki', label: '🌐 Cisco Meraki' },
  { value: 'tp_link', label: '🌐 TP-Link' },
  { value: 'tenda', label: '🌐 Tenda' },
  { value: 'mikrotik', label: '🌐 Mikrotik RouterOS' }
];

const URL_EXAMPLES: Record<string, string> = {
  unifi: 'https://192.168.1.1:8443',
  meraki: 'https://api.meraki.com/api/v1',
  tp_link: 'http://192.168.1.1',
  tenda: 'http://tendawifi.com',
  mikrotik: 'http://192.168.1.1:8728'
};

export default function NetworkSettingsPage() {
  const [config, setConfig] = useState<WiFiConfig | null>(null);
  const [policies, setPolicies] = useState<NetworkPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'detect' | 'manual' | 'done'>('detect');

  const [detecting, setDetecting] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);

  const [manualForm, setManualForm] = useState({
    router_type: 'tenda',
    router_url: 'http://tendawifi.com',
    router_username: 'admin',
    router_password: ''
  });

  const [policyForm, setPolicyForm] = useState({
    name: '',
    description: '',
    block_categories: [] as string[]
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiUrl}/network/wifi-config`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setConfig(await res.json());
        setStep('done');
      } else {
        setStep('detect');
      }

      const policiesRes = await fetch(`${apiUrl}/network/policies`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (policiesRes.ok) {
        setPolicies(await policiesRes.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectRouter = async () => {
    try {
      setDetecting(true);
      const res = await fetch(`${apiUrl}/network/wifi-config/detect`, {
        method: 'POST'
      });

      const result = await res.json();

      if (result.detected) {
        alert(`✅ Found ${result.router_type.toUpperCase()} at ${result.router_url}`);
        setManualForm({
          router_type: result.router_type,
          router_url: result.router_url,
          router_username: 'admin',
          router_password: ''
        });
        setStep('manual');
      } else {
        alert('Could not auto-detect. Entering manual mode...');
        setStep('manual');
      }
    } catch (err) {
      alert('Detection failed. Entering manual mode...');
      setStep('manual');
    } finally {
      setDetecting(false);
    }
  };

  const handleSaveRouter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualForm.router_password) {
      alert('Please enter your router password');
      return;
    }

    try {
      setTestingConnection(true);

      // Test connection
      const testRes = await fetch(`${apiUrl}/network/wifi-config/test-connection`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          router_url: manualForm.router_url,
          password: manualForm.router_password,
          router_type: manualForm.router_type
        })
      });

      const testResult = await testRes.json();

      if (testResult.success) {
        // Save config
        const saveRes = await fetch(`${apiUrl}/network/wifi-config`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(manualForm)
        });

        if (saveRes.ok) {
          setConfig(await saveRes.json());
          setStep('done');
          alert('✅ Router configured successfully!');
        }
      } else {
        alert('❌ Connection failed: ' + (testResult.message || testResult.error));
      }
    } catch (err) {
      alert('Error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setTestingConnection(false);
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(`${apiUrl}/network/policies`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(policyForm)
      });

      if (!res.ok) throw new Error('Failed to create policy');

      alert('✅ Policy created successfully');
      setPolicyForm({ name: '', description: '', block_categories: [] });
      fetchSettings();
    } catch (err) {
      alert('❌ Error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  if (loading) return <div className="p-8 text-center">Loading settings...</div>;

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Settings className="h-8 w-8" />
          Network Settings
        </h1>
        <p className="text-gray-600">Configure your WiFi router and create access policies</p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 pt-6">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Router Configuration */}
      {step === 'detect' && !config && (
        <Card>
          <CardHeader>
            <CardTitle>🔍 Setup Your Router</CardTitle>
            <CardDescription>Auto-detect or manually configure</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={handleDetectRouter}
              disabled={detecting}
              className="w-full"
              size="lg"
            >
              {detecting ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Scanning Network...
                </>
              ) : (
                '🔍 Detect My Router'
              )}
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-gray-500">or</span>
              </div>
            </div>

            <Button
              variant="outline"
              onClick={() => setStep('manual')}
              className="w-full"
              size="lg"
            >
              📝 Enter Manually
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Manual Configuration */}
      {step === 'manual' && !config && (
        <Card>
          <CardHeader>
            <CardTitle>📝 Configure Router</CardTitle>
            <CardDescription>Enter your WiFi router details</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveRouter} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Router Type *</label>
                <select
                  value={manualForm.router_type}
                  onChange={(e) =>
                    setManualForm({
                      ...manualForm,
                      router_type: e.target.value,
                      router_url: URL_EXAMPLES[e.target.value] || ''
                    })
                  }
                  className="mt-1 block w-full rounded border px-3 py-2"
                  required
                >
                  {ROUTER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium">Router URL *</label>
                <input
                  type="text"
                  value={manualForm.router_url}
                  onChange={(e) =>
                    setManualForm({ ...manualForm, router_url: e.target.value })
                  }
                  placeholder="http://tendawifi.com"
                  className="mt-1 block w-full rounded border px-3 py-2"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">
                  Example: {URL_EXAMPLES[manualForm.router_type]}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium">Username</label>
                <input
                  type="text"
                  value={manualForm.router_username}
                  onChange={(e) =>
                    setManualForm({ ...manualForm, router_username: e.target.value })
                  }
                  placeholder="admin"
                  className="mt-1 block w-full rounded border px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium">Password *</label>
                <input
                  type="password"
                  value={manualForm.router_password}
                  onChange={(e) =>
                    setManualForm({ ...manualForm, router_password: e.target.value })
                  }
                  placeholder="Your router admin password"
                  className="mt-1 block w-full rounded border px-3 py-2"
                  required
                />
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={testingConnection} className="flex-1">
                  {testingConnection ? (
                    <>
                      <Loader className="mr-2 h-4 w-4 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    '🔗 Test & Save'
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setStep('detect');
                    setManualForm({
                      router_type: 'tenda',
                      router_url: 'http://tendawifi.com',
                      router_username: 'admin',
                      router_password: ''
                    });
                  }}
                >
                  Back
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Connected Status */}
      {step === 'done' && config && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800">
              <Check className="h-5 w-5" />
              ✅ Router Connected
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <span className="font-semibold">Type:</span> {config.router_type.toUpperCase()}
            </p>
            <p>
              <span className="font-semibold">URL:</span> {config.router_url}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setStep('detect');
                setManualForm({
                  router_type: 'tenda',
                  router_url: 'http://tendawifi.com',
                  router_username: 'admin',
                  router_password: ''
                });
              }}
            >
              Change Router
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Network Policies */}
      <Card>
        <CardHeader>
          <CardTitle>🚫 Network Policies</CardTitle>
          <CardDescription>Block categories of websites</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {policies.length > 0 && (
            <div className="space-y-2">
              {policies.map((policy) => (
                <div key={policy.id} className="rounded border border-blue-200 bg-blue-50 p-3">
                  <p className="font-semibold">{policy.name}</p>
                  <p className="text-sm text-gray-600">{policy.description}</p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {policy.block_categories.map((cat) => (
                      <span
                        key={cat}
                        className="inline-block rounded bg-red-100 px-2 py-1 text-xs text-red-800"
                      >
                        ❌ {cat}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <form onSubmit={handleCreatePolicy} className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Create New Policy</h3>

            <div>
              <label className="block text-sm font-medium">Policy Name *</label>
              <input
                type="text"
                placeholder="e.g., Block Adult Content"
                value={policyForm.name}
                onChange={(e) => setPolicyForm({ ...policyForm, name: e.target.value })}
                className="mt-1 block w-full rounded border px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Description</label>
              <input
                type="text"
                placeholder="Policy description"
                value={policyForm.description}
                onChange={(e) =>
                  setPolicyForm({ ...policyForm, description: e.target.value })
                }
                className="mt-1 block w-full rounded border px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Block Categories</label>
              <div className="mt-2 space-y-2">
                {DOMAIN_CATEGORIES.map((cat) => (
                  <label key={cat.value} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={policyForm.block_categories.includes(cat.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: [...policyForm.block_categories, cat.value]
                          });
                        } else {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: policyForm.block_categories.filter(
                              (c) => c !== cat.value
                            )
                          });
                        }
                      }}
                    />
                    <span>{cat.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <Button
              type="submit"
              disabled={!policyForm.name || policyForm.block_categories.length === 0}
            >
              Create Policy
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
